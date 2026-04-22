import json
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from app.repositories.pedido_repository import pedido_repository
from app.repositories.cliente_repository import cliente_repository
from app.repositories.disco_repository import disco_repository
from app.schemas.pedido_schema import (
    PedidoCreate,
    PedidoResponse,
    PedidoEnqueuedResponse,
    PaginatedPedidos,
    PedidoFilter,
)
from app.models.pedido import PedidoStatus
from app.infra.redis_client import get_redis
from app.core.config import settings
from sqlalchemy import func
from app.models.pedido import Pedido
from app.models.item_pedido import ItemPedido
from app.models.disco import Disco


class PedidoService:

    # ------------------------------------------------------------------
    # Enqueue (called by the HTTP endpoint — fast path)
    # ------------------------------------------------------------------

    def enqueue(self, db: Session, data: PedidoCreate) -> PedidoEnqueuedResponse:
        # --- Idempotency check ---
        if data.idempotency_key:
            existing = pedido_repository.get_by_idempotency_key(db, data.idempotency_key)
            if existing:
                return PedidoEnqueuedResponse(
                    pedido_id=existing.id,
                    status=existing.status,
                    mensagem="Pedido já recebido anteriormente (idempotency_key duplicada).",
                )

        # --- Validate cliente ---
        cliente = cliente_repository.get_by_id(db, data.cliente_id)
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
        if not cliente.ativo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cliente inativo não pode realizar pedidos.",
            )

        # --- Validate all discos exist (fast pre-check before DB write) ---
        for item in data.itens:
            disco = disco_repository.get_by_id(db, item.disco_id)
            if not disco:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Disco id={item.disco_id} não encontrado.",
                )

        # --- Persist pedido with PENDING status ---
        pedido = pedido_repository.create_pending(
            db=db,
            cliente_id=data.cliente_id,
            itens=[i.model_dump() for i in data.itens],
            idempotency_key=data.idempotency_key,
        )

        # --- Push pedido_id to Redis queue ---
        r = get_redis()
        r.lpush(settings.PEDIDO_QUEUE_KEY, pedido.id)

        return PedidoEnqueuedResponse(pedido_id=pedido.id, status=PedidoStatus.PENDING)

    # ------------------------------------------------------------------
    # Status query (polling endpoint)
    # ------------------------------------------------------------------

    def get_status(self, db: Session, pedido_id: int) -> PedidoResponse:
        pedido = pedido_repository.get_by_id(db, pedido_id)
        if not pedido:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
        return PedidoResponse.model_validate(pedido)

    # ------------------------------------------------------------------
    # List with filters
    # ------------------------------------------------------------------

    def list(self, db: Session, filters: PedidoFilter) -> PaginatedPedidos:
        total, pedidos = pedido_repository.list(
            db,
            cliente_id=filters.cliente_id,
            data_inicio=filters.data_inicio,
            data_fim=filters.data_fim,
            status=filters.status,
            page=filters.page,
            page_size=filters.page_size,
        )
        return PaginatedPedidos(
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            items=[PedidoResponse.model_validate(p) for p in pedidos],
        )

    # ------------------------------------------------------------------
    # Stock processing (called exclusively by the worker — not the API)
    # ------------------------------------------------------------------

    def process_stock(self, db: Session, pedido_id: int) -> None:
        """
        Core concurrency-safe processing:
        1. Load pedido + itens from DB
        2. For each item: DECRBY in Redis (atomic)
           - If result < 0 → INCRBY rollback → mark FAILED
        3. On success: decrement DB stocks, mark COMPLETED
        """
        pedido = pedido_repository.get_by_id(db, pedido_id)
        if not pedido:
            return  # Already cleaned up or ghost message

        if pedido.status != PedidoStatus.PENDING:
            return  # Already processed (duplicate message guard)

        # Mark as PROCESSING to prevent duplicate processing
        pedido_repository.update_status(db, pedido, PedidoStatus.PROCESSING)

        r = get_redis()
        decremented: list[tuple[int, int]] = []  # (disco_id, quantidade) — for rollback

        try:
            for item in pedido.itens:
                stock_key = f"{settings.STOCK_KEY_PREFIX}:{item.disco_id}"
                new_stock = r.decrby(stock_key, item.quantidade)

                if new_stock < 0:
                    # Rollback Redis for all already-decremented items
                    r.incrby(stock_key, item.quantidade)
                    for prev_disco_id, prev_qty in decremented:
                        r.incrby(f"{settings.STOCK_KEY_PREFIX}:{prev_disco_id}", prev_qty)

                    pedido_repository.update_status(
                        db, pedido, PedidoStatus.FAILED,
                        motivo_falha=f"Estoque insuficiente para disco id={item.disco_id}.",
                    )
                    return

                decremented.append((item.disco_id, item.quantidade))

            # All stock deducted — now sync to DB
            for disco_id, quantidade in decremented:
                disco_repository.decrement_stock_db(db, disco_id, quantidade)

            db.commit()
            pedido_repository.update_status(db, pedido, PedidoStatus.COMPLETED)

        except Exception as exc:
            # Unexpected error — rollback Redis and mark failed
            for prev_disco_id, prev_qty in decremented:
                r.incrby(f"{settings.STOCK_KEY_PREFIX}:{prev_disco_id}", prev_qty)
            pedido_repository.update_status(
                db, pedido, PedidoStatus.FAILED,
                motivo_falha=f"Erro interno: {str(exc)}",
            )
            raise

    # ------------------------------------------------------------------
    # Reset (Admin clear queue & orders)
    # ------------------------------------------------------------------

    def reset_all(self, db: Session) -> None:
        # 1. Sum up quantities from COMPLETED orders
        completed_items = (
            db.query(ItemPedido.disco_id, func.sum(ItemPedido.quantidade).label("total_qty"))
            .join(Pedido)
            .filter(Pedido.status == PedidoStatus.COMPLETED)
            .group_by(ItemPedido.disco_id)
            .all()
        )

        # 2. Add back to Disco.quantidade
        for disco_id, total_qty in completed_items:
            db.query(Disco).filter(Disco.id == disco_id).update(
                {Disco.quantidade: Disco.quantidade + total_qty}
            )

        # 3. Delete all items and orders
        db.query(ItemPedido).delete()
        db.query(Pedido).delete()
        db.commit()

        # 4. Clear Redis queues
        r = get_redis()
        r.delete(settings.PEDIDO_QUEUE_KEY)
        r.delete(settings.PEDIDO_DEAD_QUEUE_KEY)

        # 5. Restore Redis stock keys
        _, discos = disco_repository.list(db, page_size=1000)
        for disco in discos:
            r.set(f"{settings.STOCK_KEY_PREFIX}:{disco.id}", disco.quantidade)


pedido_service = PedidoService()

