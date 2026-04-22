from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Disco(Base):
    __tablename__ = "discos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    artista = Column(String(255), nullable=False, index=True)
    ano_lancamento = Column(Integer, nullable=False, index=True)
    estilo = Column(String(100), nullable=False, index=True)
    quantidade = Column(Integer, nullable=False, default=0)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    itens = relationship("ItemPedido", back_populates="disco")
