from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.disco_service import disco_service
from app.schemas.disco_schema import (
    DiscoCreate, DiscoUpdate, DiscoResponse, PaginatedDiscos
)

router = APIRouter(prefix="/discos", tags=["Discos"])


@router.get("", response_model=PaginatedDiscos)
def list_discos(
    nome: Optional[str] = Query(None),
    artista: Optional[str] = Query(None),
    ano_lancamento: Optional[int] = Query(None),
    estilo: Optional[str] = Query(None),
    include_inactive: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return disco_service.list(db, nome, artista, ano_lancamento, estilo, include_inactive, page, page_size)


@router.get("/{disco_id}", response_model=DiscoResponse)
def get_disco(disco_id: int, db: Session = Depends(get_db)):
    return disco_service.get_by_id(db, disco_id)


@router.post("", response_model=DiscoResponse, status_code=201)
def create_disco(data: DiscoCreate, db: Session = Depends(get_db)):
    return disco_service.create(db, data)


@router.put("/{disco_id}", response_model=DiscoResponse)
def update_disco(disco_id: int, data: DiscoUpdate, db: Session = Depends(get_db)):
    return disco_service.update(db, disco_id, data)


@router.delete("/{disco_id}", response_model=DiscoResponse)
def delete_disco(disco_id: int, db: Session = Depends(get_db)):
    return disco_service.delete(db, disco_id)
