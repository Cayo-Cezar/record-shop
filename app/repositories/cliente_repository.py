from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.cliente import Cliente


class ClienteRepository:

    def get_by_id(self, db: Session, cliente_id: int) -> Optional[Cliente]:
        return db.query(Cliente).filter(Cliente.id == cliente_id).first()

    def get_by_documento(self, db: Session, documento: str) -> Optional[Cliente]:
        return db.query(Cliente).filter(Cliente.documento == documento).first()

    def get_by_email(self, db: Session, email: str) -> Optional[Cliente]:
        return db.query(Cliente).filter(Cliente.email == email).first()

    def list(self, db: Session) -> List[Cliente]:
        return db.query(Cliente).all()

    def create(self, db: Session, data: dict) -> Cliente:
        cliente = Cliente(**data)
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        return cliente

    def update(self, db: Session, cliente: Cliente, data: dict) -> Cliente:
        for key, value in data.items():
            setattr(cliente, key, value)
        db.commit()
        db.refresh(cliente)
        return cliente

    def inativar(self, db: Session, cliente: Cliente) -> Cliente:
        cliente.ativo = False
        db.commit()
        db.refresh(cliente)
        return cliente

    def reativar(self, db: Session, cliente: Cliente) -> Cliente:
        cliente.ativo = True
        db.commit()
        db.refresh(cliente)
        return cliente


cliente_repository = ClienteRepository()
