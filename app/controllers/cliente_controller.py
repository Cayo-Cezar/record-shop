from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.cliente_service import cliente_service
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate, ClienteResponse

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("", response_model=List[ClienteResponse])
def list_clientes(db: Session = Depends(get_db)):
    return cliente_service.list(db)


@router.get("/{cliente_id}", response_model=ClienteResponse)
def get_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return cliente_service.get_by_id(db, cliente_id)


@router.post("", response_model=ClienteResponse, status_code=201)
def create_cliente(data: ClienteCreate, db: Session = Depends(get_db)):
    return cliente_service.create(db, data)


@router.put("/{cliente_id}", response_model=ClienteResponse)
def update_cliente(cliente_id: int, data: ClienteUpdate, db: Session = Depends(get_db)):
    return cliente_service.update(db, cliente_id, data)


@router.patch("/{cliente_id}/inativar", response_model=ClienteResponse)
def inativar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return cliente_service.inativar(db, cliente_id)


@router.patch("/{cliente_id}/reativar", response_model=ClienteResponse)
def reativar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return cliente_service.reativar(db, cliente_id)
