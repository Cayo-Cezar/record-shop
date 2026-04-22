from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from app.repositories.cliente_repository import cliente_repository
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate, ClienteResponse


class ClienteService:

    def get_by_id(self, db: Session, cliente_id: int) -> ClienteResponse:
        cliente = cliente_repository.get_by_id(db, cliente_id)
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
        return ClienteResponse.model_validate(cliente)

    def list(self, db: Session) -> List[ClienteResponse]:
        clientes = cliente_repository.list(db)
        return [ClienteResponse.model_validate(c) for c in clientes]

    def create(self, db: Session, data: ClienteCreate) -> ClienteResponse:
        # Uniqueness checks
        if cliente_repository.get_by_documento(db, data.documento):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um cliente com este documento.",
            )
        if cliente_repository.get_by_email(db, str(data.email)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um cliente com este e-mail.",
            )

        cliente = cliente_repository.create(db, data.model_dump())
        return ClienteResponse.model_validate(cliente)

    def update(self, db: Session, cliente_id: int, data: ClienteUpdate) -> ClienteResponse:
        cliente = cliente_repository.get_by_id(db, cliente_id)
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
        if not cliente.ativo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível atualizar um cliente inativo.",
            )

        updates = data.model_dump(exclude_none=True)

        # E-mail uniqueness (if being changed)
        if "email" in updates:
            existing = cliente_repository.get_by_email(db, str(updates["email"]))
            if existing and existing.id != cliente_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="E-mail já em uso por outro cliente.",
                )

        cliente = cliente_repository.update(db, cliente, updates)
        return ClienteResponse.model_validate(cliente)

    def inativar(self, db: Session, cliente_id: int) -> ClienteResponse:
        cliente = cliente_repository.get_by_id(db, cliente_id)
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
        if not cliente.ativo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cliente já está inativo.",
            )

        cliente = cliente_repository.inativar(db, cliente)
        return ClienteResponse.model_validate(cliente)

    def reativar(self, db: Session, cliente_id: int) -> ClienteResponse:
        cliente = cliente_repository.get_by_id(db, cliente_id)
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
        if cliente.ativo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cliente já está ativo.",
            )

        cliente = cliente_repository.reativar(db, cliente)
        return ClienteResponse.model_validate(cliente)


cliente_service = ClienteService()
