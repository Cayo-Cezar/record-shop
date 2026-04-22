from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False, index=True)
    disco_id = Column(Integer, ForeignKey("discos.id"), nullable=False, index=True)
    quantidade = Column(Integer, nullable=False)

    pedido = relationship("Pedido", back_populates="itens")
    disco = relationship("Disco", back_populates="itens")
