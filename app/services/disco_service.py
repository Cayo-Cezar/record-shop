from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, Tuple, List

from app.models.disco import Disco
from app.repositories.disco_repository import disco_repository
from app.schemas.disco_schema import DiscoCreate, DiscoUpdate, DiscoResponse, PaginatedDiscos
from app.infra.redis_client import (
    get_redis, cache_get, cache_set, cache_delete, cache_delete_pattern, make_list_cache_key
)
from app.core.config import settings


class DiscoService:

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def _entity_key(self, disco_id: int) -> str:
        return f"{settings.DISCO_CACHE_PREFIX}:{disco_id}"

    def _invalidate_all(self, disco_id: Optional[int] = None) -> None:
        """Invalidate entity cache and all list caches."""
        if disco_id:
            cache_delete(self._entity_key(disco_id))
        cache_delete_pattern(f"{settings.DISCO_LIST_CACHE_PREFIX}:*")

    # ------------------------------------------------------------------
    # Stock seed (called at startup)
    # ------------------------------------------------------------------

    def seed_stock_to_redis(self, db: Session) -> None:
        """Load all active disco stocks into Redis for atomic control."""
        r = get_redis()
        stocks = disco_repository.get_all_active_stocks(db)
        pipe = r.pipeline()
        for disco_id, quantidade in stocks:
            key = f"{settings.STOCK_KEY_PREFIX}:{disco_id}"
            pipe.set(key, quantidade)
        pipe.execute()
        print(f"✅ Estoque de {len(stocks)} disco(s) carregado no Redis")

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def get_by_id(self, db: Session, disco_id: int) -> DiscoResponse:
        # Try entity cache
        cached = cache_get(self._entity_key(disco_id))
        if cached:
            return DiscoResponse(**cached)

        disco = disco_repository.get_by_id(db, disco_id)
        if not disco:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disco não encontrado")

        response = DiscoResponse.model_validate(disco)
        cache_set(self._entity_key(disco_id), response.model_dump(), settings.DISCO_CACHE_TTL)
        return response

    def list(
        self,
        db: Session,
        nome: Optional[str],
        artista: Optional[str],
        ano_lancamento: Optional[int],
        estilo: Optional[str],
        include_inactive: bool,
        page: int,
        page_size: int,
    ) -> PaginatedDiscos:
        cache_key = make_list_cache_key(
            settings.DISCO_LIST_CACHE_PREFIX,
            nome=nome, artista=artista,
            ano_lancamento=ano_lancamento, estilo=estilo,
            include_inactive=include_inactive,
            page=page, page_size=page_size,
        )

        cached = cache_get(cache_key)
        if cached:
            return PaginatedDiscos(**cached)

        total, discos = disco_repository.list(
            db, nome=nome, artista=artista,
            ano_lancamento=ano_lancamento, estilo=estilo,
            include_inactive=include_inactive,
            page=page, page_size=page_size,
        )
        result = PaginatedDiscos(
            total=total,
            page=page,
            page_size=page_size,
            items=[DiscoResponse.model_validate(d) for d in discos],
        )
        cache_set(cache_key, result.model_dump(), settings.DISCO_LIST_CACHE_TTL)
        return result

    def create(self, db: Session, data: DiscoCreate) -> DiscoResponse:
        disco = disco_repository.create(db, data.model_dump())

        # Seed the new disco stock into Redis immediately
        r = get_redis()
        r.set(f"{settings.STOCK_KEY_PREFIX}:{disco.id}", disco.quantidade)

        self._invalidate_all()
        return DiscoResponse.model_validate(disco)

    def update(self, db: Session, disco_id: int, data: DiscoUpdate) -> DiscoResponse:
        disco = disco_repository.get_by_id_any_status(db, disco_id)
        if not disco:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disco não encontrado")

        updates = data.model_dump(exclude_none=True)
        disco = disco_repository.update(db, disco, updates)

        # If quantity changed, sync Redis stock
        if "quantidade" in updates:
            r = get_redis()
            r.set(f"{settings.STOCK_KEY_PREFIX}:{disco.id}", disco.quantidade)

        self._invalidate_all(disco_id)
        return DiscoResponse.model_validate(disco)

    def delete(self, db: Session, disco_id: int) -> DiscoResponse:
        disco = disco_repository.get_by_id(db, disco_id)
        if not disco:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disco não encontrado")

        disco = disco_repository.delete(db, disco)
        self._invalidate_all(disco_id)
        return DiscoResponse.model_validate(disco)


disco_service = DiscoService()
