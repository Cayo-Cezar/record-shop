from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    documento = Column(String(20), unique=True, nullable=False, index=True)
    nome_completo = Column(String(255), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefone = Column(String(20), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    pedidos = relationship("Pedido", back_populates="cliente")
