"""
seed.py — Lea Record Shop
=========================
Popula o banco e o Redis com dados do cenário descrito no desafio:
  • Disco "We Are Reactive" da Hohpe — 500 unidades (o lançamento)
  • Mais 6 discos variados para deixar o catálogo realista
  • 5 clientes de exemplo prontos para fazer pedidos

Como rodar:
    # Localmente (com .env ou variáveis exportadas)
    python seed.py

    # Dentro do container da API
    docker exec lea_api python seed.py

    # Via docker compose
    docker compose exec api python seed.py
"""

import os
import sys
from datetime import date

# ── Garante que o diretório raiz do projeto está no path ──────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models import Cliente, Disco, Pedido, ItemPedido   # noqa — registra modelos
from app.infra.redis_client import get_redis
from app.core.config import settings


# ══════════════════════════════════════════════════════════════════════════
# DADOS SEED
# ══════════════════════════════════════════════════════════════════════════

DISCOS_SEED = [
    # ★ DISCO DO LANÇAMENTO — conforme o PDF
    {
        "nome":            "We Are Reactive",
        "artista":         "Hohpe",
        "ano_lancamento":  2024,
        "estilo":          "Indie",
        "quantidade":      500,
    },
    # Outros discos para deixar o catálogo interessante
    {
        "nome":            "Dark Side of the Moon",
        "artista":         "Pink Floyd",
        "ano_lancamento":  1973,
        "estilo":          "Rock Progressivo",
        "quantidade":      120,
    },
    {
        "nome":            "Kind of Blue",
        "artista":         "Miles Davis",
        "ano_lancamento":  1959,
        "estilo":          "Jazz",
        "quantidade":      80,
    },
    {
        "nome":            "Thriller",
        "artista":         "Michael Jackson",
        "ano_lancamento":  1982,
        "estilo":          "Pop",
        "quantidade":      200,
    },
    {
        "nome":            "Random Access Memories",
        "artista":         "Daft Punk",
        "ano_lancamento":  2013,
        "estilo":          "Eletrônico",
        "quantidade":      60,
    },
    {
        "nome":            "Minha Fé",
        "artista":         "Djavan",
        "ano_lancamento":  1987,
        "estilo":          "MPB",
        "quantidade":      45,
    },
    {
        "nome":            "Construção",
        "artista":         "Chico Buarque",
        "ano_lancamento":  1971,
        "estilo":          "MPB",
        "quantidade":      5,   # Estoque crítico — boa demonstração visual
    },
]

CLIENTES_SEED = [
    {
        "nome_completo":    "Ana Beatriz Ferreira",
        "documento":        "11122233344",
        "data_nascimento":  date(1992, 5, 14),
        "email":            "ana.ferreira@email.com",
        "telefone":         "11999110001",
    },
    {
        "nome_completo":    "Carlos Eduardo Lima",
        "documento":        "22233344455",
        "data_nascimento":  date(1988, 11, 3),
        "email":            "carlos.lima@email.com",
        "telefone":         "21988220002",
    },
    {
        "nome_completo":    "Fernanda Souza",
        "documento":        "33344455566",
        "data_nascimento":  date(1995, 7, 22),
        "email":            "fernanda.souza@email.com",
        "telefone":         "31977330003",
    },
    {
        "nome_completo":    "Rafael Mendes",
        "documento":        "44455566677",
        "data_nascimento":  date(1990, 2, 8),
        "email":            "rafael.mendes@email.com",
        "telefone":         None,
    },
    {
        "nome_completo":    "Juliana Costa",
        "documento":        "55566677788",
        "data_nascimento":  date(2000, 9, 30),
        "email":            "juliana.costa@email.com",
        "telefone":         "41966440004",
    },
]


# ══════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════

RESET  = "\033[0m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
RED    = "\033[31m"
BOLD   = "\033[1m"

def ok(msg):    print(f"  {GREEN}✓{RESET} {msg}")
def skip(msg):  print(f"  {YELLOW}~{RESET} {msg} (já existe, ignorado)")
def info(msg):  print(f"  {CYAN}•{RESET} {msg}")
def error(msg): print(f"  {RED}✗{RESET} {msg}")


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

def run_seed():
    print(f"\n{BOLD}{'═'*52}{RESET}")
    print(f"{BOLD}  Lea Record Shop — Seed{RESET}")
    print(f"{BOLD}{'═'*52}{RESET}\n")

    # Garante que as tabelas existem
    Base.metadata.create_all(bind=engine)
    info("Tabelas verificadas/criadas\n")

    db = SessionLocal()

    try:
        # ── DISCOS ──────────────────────────────────────────────
        print(f"{BOLD}Discos{RESET}")
        criados_discos = []
        for d in DISCOS_SEED:
            existe = db.query(Disco).filter(
                Disco.nome == d["nome"],
                Disco.artista == d["artista"],
            ).first()
            if existe:
                skip(f"{d['artista']} — {d['nome']}")
                criados_discos.append(existe)
            else:
                disco = Disco(**d)
                db.add(disco)
                db.flush()
                ok(f"{d['artista']} — {d['nome']}  ({d['quantidade']} un.)")
                criados_discos.append(disco)

        db.commit()

        # ── CLIENTES ─────────────────────────────────────────────
        print(f"\n{BOLD}Clientes{RESET}")
        for c in CLIENTES_SEED:
            existe = db.query(Cliente).filter(
                Cliente.documento == c["documento"]
            ).first()
            if existe:
                skip(c["nome_completo"])
            else:
                db.add(Cliente(**c))
                ok(c["nome_completo"])

        db.commit()

        # ── REDIS STOCK SEED ─────────────────────────────────────
        print(f"\n{BOLD}Redis — estoque{RESET}")
        r = get_redis()
        pipe = r.pipeline()
        for disco in criados_discos:
            key = f"{settings.STOCK_KEY_PREFIX}:{disco.id}"
            pipe.set(key, disco.quantidade)

        pipe.execute()

        # Confirma no log
        for disco in criados_discos:
            val = r.get(f"{settings.STOCK_KEY_PREFIX}:{disco.id}")
            ok(f"estoque:{disco.id}  →  {val} unidades  [{disco.nome}]")

        # ── SUMMARY ──────────────────────────────────────────────
        total_discos   = db.query(Disco).count()
        total_clientes = db.query(Cliente).count()

        print(f"\n{BOLD}{'─'*52}{RESET}")
        print(f"{BOLD}  Resumo{RESET}")
        print(f"{'─'*52}")
        info(f"Discos no banco:    {total_discos}")
        info(f"Clientes no banco:  {total_clientes}")
        info(f"Chaves Redis:       {len(criados_discos)} estoques\n")

        launch = next((d for d in criados_discos if d.nome == "We Are Reactive"), None)
        if launch:
            stock_redis = r.get(f"{settings.STOCK_KEY_PREFIX}:{launch.id}")
            print(f"{BOLD}  🎵 Disco do lançamento{RESET}")
            print(f"     ID:       {launch.id}")
            print(f"     Nome:     {launch.nome} — {launch.artista}")
            print(f"     Estilo:   {launch.estilo}")
            print(f"     Estoque:  {stock_redis} unidades no Redis")
            print(f"\n  Para simular o lançamento (50 req/s):")
            print(f"{CYAN}  hey -n 500 -c 50 -m POST \\")
            print(f"    -H 'Content-Type: application/json' \\")
            print(f"    -d '{{\"cliente_id\":1,\"itens\":[{{\"disco_id\":{launch.id},\"quantidade\":1}}]}}' \\")
            print(f"    http://localhost:8000/pedidos{RESET}")

        print(f"\n{GREEN}{BOLD}  Seed concluído com sucesso! ✓{RESET}\n")

    except Exception as exc:
        db.rollback()
        error(f"Erro durante o seed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
