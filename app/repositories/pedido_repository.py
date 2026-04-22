from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, Tuple, List
from datetime import datetime
from app.models.pedido import Pedido, PedidoStatus
from app.models.item_pedido import ItemPedido


class PedidoRepository:

    def get_by_id(self, db: Session, pedido_id: int) -> Optional[Pedido]:
        return (
            db.query(Pedido)
            .options(joinedload(Pedido.itens))
            .filter(Pedido.id == pedido_id)
            .first()
        )

    def get_by_idempotency_key(self, db: Session, key: str) -> Optional[Pedido]:
        return db.query(Pedido).filter(Pedido.idempotency_key == key).first()

    def list(
        self,
        db: Session,
        cliente_id: Optional[int] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        status: Optional[PedidoStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[int, List[Pedido]]:
        query = db.query(Pedido).options(joinedload(Pedido.itens))

        if cliente_id:
            query = query.filter(Pedido.cliente_id == cliente_id)
        if data_inicio:
            query = query.filter(Pedido.criado_em >= data_inicio)
        if data_fim:
            query = query.filter(Pedido.criado_em <= data_fim)
        if status:
            query = query.filter(Pedido.status == status)

        total = query.with_entities(func.count()).scalar()
        items = (
            query.order_by(Pedido.criado_em.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return total, items

    def create_pending(
        self,
        db: Session,
        cliente_id: int,
        itens: List[dict],
        idempotency_key: Optional[str] = None,
    ) -> Pedido:
        """Create pedido + itens with PENDING status in a single transaction."""
        pedido = Pedido(
            cliente_id=cliente_id,
            status=PedidoStatus.PENDING,
            idempotency_key=idempotency_key,
        )
        db.add(pedido)
        db.flush()  # Get pedido.id without committing

        for item in itens:
            db.add(ItemPedido(
                pedido_id=pedido.id,
                disco_id=item["disco_id"],
                quantidade=item["quantidade"],
            ))

        db.commit()
        db.refresh(pedido)
        return pedido

    def update_status(
        self,
        db: Session,
        pedido: Pedido,
        status: PedidoStatus,
        motivo_falha: Optional[str] = None,
    ) -> Pedido:
        pedido.status = status
        if motivo_falha:
            pedido.motivo_falha = motivo_falha
        db.commit()
        db.refresh(pedido)
        return pedido


pedido_repository = PedidoRepository()
