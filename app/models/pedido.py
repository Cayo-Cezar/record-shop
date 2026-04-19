from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    criado_em = Column(DateTime, default=datetime.utcnow)

    cliente = relationship("Cliente")
    itens = relationship("ItemPedido", back_populates="pedido")