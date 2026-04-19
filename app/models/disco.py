from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class Disco(Base):
    __tablename__ = "discos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    artista = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, nullable=False)