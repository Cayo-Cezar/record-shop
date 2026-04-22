from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date, datetime
from typing import Optional


class ClienteBase(BaseModel):
    documento: str = Field(..., min_length=11, max_length=20)
    nome_completo: str = Field(..., min_length=2, max_length=255)
    data_nascimento: date
    email: EmailStr
    telefone: Optional[str] = Field(None, max_length=20)

    @field_validator("documento")
    @classmethod
    def documento_only_digits(cls, v: str) -> str:
        digits = v.replace(".", "").replace("-", "").replace("/", "")
        if not digits.isdigit():
            raise ValueError("Documento deve conter apenas dígitos")
        return digits


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome_completo: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=20)
    data_nascimento: Optional[date] = None


class ClienteResponse(ClienteBase):
    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}
