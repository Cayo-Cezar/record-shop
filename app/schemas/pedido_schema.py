from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.pedido import PedidoStatus


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

class ItemPedidoCreate(BaseModel):
    disco_id: int = Field(..., ge=1)
    quantidade: int = Field(..., ge=1)


class PedidoCreate(BaseModel):
    cliente_id: int = Field(..., ge=1)
    itens: List[ItemPedidoCreate] = Field(..., min_length=1)
    idempotency_key: Optional[str] = Field(None, max_length=64)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

class ItemPedidoResponse(BaseModel):
    disco_id: int
    quantidade: int

    model_config = {"from_attributes": True}


class PedidoResponse(BaseModel):
    id: int
    cliente_id: int
    status: PedidoStatus
    motivo_falha: Optional[str]
    idempotency_key: Optional[str]
    criado_em: datetime
    itens: List[ItemPedidoResponse]

    model_config = {"from_attributes": True}


class PedidoEnqueuedResponse(BaseModel):
    """Returned immediately after enqueuing — before the worker processes."""
    pedido_id: int
    status: PedidoStatus
    mensagem: str = "Pedido recebido e enfileirado para processamento."


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

class PedidoFilter(BaseModel):
    cliente_id: Optional[int] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    status: Optional[PedidoStatus] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PaginatedPedidos(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[PedidoResponse]
