from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List


class DiscoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    artista: str = Field(..., min_length=1, max_length=255)
    ano_lancamento: int = Field(..., ge=1900, le=2100)
    estilo: str = Field(..., min_length=1, max_length=100)
    quantidade: int = Field(..., ge=0)


class DiscoCreate(DiscoBase):
    pass


class DiscoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    artista: Optional[str] = Field(None, min_length=1, max_length=255)
    ano_lancamento: Optional[int] = Field(None, ge=1900, le=2100)
    estilo: Optional[str] = Field(None, min_length=1, max_length=100)
    quantidade: Optional[int] = Field(None, ge=0)
    ativo: Optional[bool] = None  # permite reativar um disco inativado


class DiscoResponse(DiscoBase):
    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}


class DiscoFilter(BaseModel):
    nome: Optional[str] = None
    artista: Optional[str] = None
    ano_lancamento: Optional[int] = None
    estilo: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PaginatedDiscos(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[DiscoResponse]
