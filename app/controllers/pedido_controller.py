from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.services.pedido_service import pedido_service
from app.schemas.pedido_schema import (
    PedidoCreate,
    PedidoResponse,
    PedidoEnqueuedResponse,
    PaginatedPedidos,
    PedidoFilter,
)
from app.models.pedido import PedidoStatus

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/reset", status_code=200)
def reset_pedidos(db: Session = Depends(get_db)):
    """
    Clear all orders, clear Redis queues, and restore stock.
    """
    pedido_service.reset_all(db)
    return {"message": "Pedidos resetados e estoque restaurado."}


@router.post("", response_model=PedidoEnqueuedResponse, status_code=202)
def create_pedido(data: PedidoCreate, db: Session = Depends(get_db)):
    """
    Enqueue a new order. Returns immediately with status=PENDING.
    The order is processed asynchronously by the worker.
    Poll GET /pedidos/{id} to check final status.
    """
    return pedido_service.enqueue(db, data)


@router.get("/{pedido_id}", response_model=PedidoResponse)
def get_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Poll the status of a previously enqueued pedido."""
    return pedido_service.get_status(db, pedido_id)


@router.get("", response_model=PaginatedPedidos)
def list_pedidos(
    cliente_id: Optional[int] = Query(None),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    status: Optional[PedidoStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    filters = PedidoFilter(
        cliente_id=cliente_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        status=status,
        page=page,
        page_size=page_size,
    )
    return pedido_service.list(db, filters)
