from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.disco_repository import disco_repository
from app.repositories.cliente_repository import cliente_repository
from app.infra.redis_client import get_redis
from app.models import Cliente, Disco, Pedido, ItemPedido
from app.core.config import settings
from datetime import date

router = APIRouter(prefix="/seed", tags=["Seed"])

# Import the seed data from seed.py logic
DISCOS_SEED = [
    {
        "nome": "We Are Reactive",
        "artista": "Hohpe",
        "ano_lancamento": 2024,
        "estilo": "Indie",
        "quantidade": 500,
    },
    {
        "nome": "Dark Side of the Moon",
        "artista": "Pink Floyd",
        "ano_lancamento": 1973,
        "estilo": "Rock",
        "quantidade": 100,
    },
    {
        "nome": "Abbey Road",
        "artista": "The Beatles",
        "ano_lancamento": 1969,
        "estilo": "Rock",
        "quantidade": 150,
    },
    {
        "nome": "Thriller",
        "artista": "Michael Jackson",
        "ano_lancamento": 1982,
        "estilo": "Pop",
        "quantidade": 200,
    },
    {
        "nome": "Back in Black",
        "artista": "AC/DC",
        "ano_lancamento": 1980,
        "estilo": "Rock",
        "quantidade": 120,
    },
    {
        "nome": "The Wall",
        "artista": "Pink Floyd",
        "ano_lancamento": 1979,
        "estilo": "Rock",
        "quantidade": 80,
    },
    {
        "nome": "Rumours",
        "artista": "Fleetwood Mac",
        "ano_lancamento": 1977,
        "estilo": "Rock",
        "quantidade": 90,
    },
]

CLIENTES_SEED = [
    {
        "nome_completo": "João Silva",
        "documento": "12345678901",
        "email": "joao.silva@example.com",
        "telefone": "(11) 99999-0001",
        "data_nascimento": date(1990, 1, 1),
    },
    {
        "nome_completo": "Maria Oliveira",
        "documento": "12345678902",
        "email": "maria.oliveira@example.com",
        "telefone": "(11) 99999-0002",
        "data_nascimento": date(1985, 5, 15),
    },
    {
        "nome_completo": "Carlos Santos",
        "documento": "12345678903",
        "email": "carlos.santos@example.com",
        "telefone": "(11) 99999-0003",
        "data_nascimento": date(1992, 3, 20),
    },
    {
        "nome_completo": "Ana Costa",
        "documento": "12345678904",
        "email": "ana.costa@example.com",
        "telefone": "(11) 99999-0004",
        "data_nascimento": date(1988, 7, 10),
    },
    {
        "nome_completo": "Pedro Lima",
        "documento": "12345678905",
        "email": "pedro.lima@example.com",
        "telefone": "(11) 99999-0005",
        "data_nascimento": date(1995, 12, 5),
    },
]


def seed_data_logic(db: Session):
    # Delete existing data
    db.query(ItemPedido).delete()
    db.query(Pedido).delete()
    db.query(Cliente).delete()
    db.query(Disco).delete()
    db.commit()

    # Seed discos
    for disco_data in DISCOS_SEED:
        disco_repository.create(db, disco_data)

    # Seed clientes
    for cliente_data in CLIENTES_SEED:
        cliente_repository.create(db, cliente_data)

    # Seed Redis stock
    redis = get_redis()
    redis.flushall()  # Clear Redis
    _, discos = disco_repository.list(db, page_size=1000)
    for disco in discos:
        redis.set(f"{settings.STOCK_KEY_PREFIX}:{disco.id}", disco.quantidade)


@router.post("")
def seed_data(db: Session = Depends(get_db)):
    seed_data_logic(db)
    return {"message": "Dados resetados e populados com sucesso."}