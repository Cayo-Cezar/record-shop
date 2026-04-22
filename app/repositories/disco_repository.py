from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Tuple, List
from app.models.disco import Disco


class DiscoRepository:

    def get_by_id(self, db: Session, disco_id: int) -> Optional[Disco]:
        return db.query(Disco).filter(Disco.id == disco_id, Disco.ativo == True).first()

    def get_by_id_any_status(self, db: Session, disco_id: int) -> Optional[Disco]:
        return db.query(Disco).filter(Disco.id == disco_id).first()

    def list(
        self,
        db: Session,
        nome: Optional[str] = None,
        artista: Optional[str] = None,
        ano_lancamento: Optional[int] = None,
        estilo: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[int, List[Disco]]:
        query = db.query(Disco).filter(Disco.ativo == True)

        if nome:
            query = query.filter(Disco.nome.ilike(f"%{nome}%"))
        if artista:
            query = query.filter(Disco.artista.ilike(f"%{artista}%"))
        if ano_lancamento:
            query = query.filter(Disco.ano_lancamento == ano_lancamento)
        if estilo:
            query = query.filter(Disco.estilo.ilike(f"%{estilo}%"))

        total = query.with_entities(func.count()).scalar()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items

    def create(self, db: Session, data: dict) -> Disco:
        disco = Disco(**data)
        db.add(disco)
        db.commit()
        db.refresh(disco)
        return disco

    def update(self, db: Session, disco: Disco, data: dict) -> Disco:
        for key, value in data.items():
            setattr(disco, key, value)
        db.commit()
        db.refresh(disco)
        return disco

    def delete(self, db: Session, disco: Disco) -> Disco:
        """Soft delete — just mark ativo=False."""
        disco.ativo = False
        db.commit()
        db.refresh(disco)
        return disco

    def get_all_active_stocks(self, db: Session) -> List[Tuple[int, int]]:
        """Returns (id, quantidade) for all active discos — used at startup."""
        return (
            db.query(Disco.id, Disco.quantidade)
            .filter(Disco.ativo == True)
            .all()
        )

    def decrement_stock_db(self, db: Session, disco_id: int, quantidade: int) -> None:
        """Decrement stock in DB after Redis already confirmed it."""
        db.query(Disco).filter(Disco.id == disco_id).update(
            {Disco.quantidade: Disco.quantidade - quantidade}
        )


disco_repository = DiscoRepository()
