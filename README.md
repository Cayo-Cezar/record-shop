# 🎵 Lea Record Shop

API de e-commerce para a loja de discos Lea Record Shop.  
Desafio técnico Backend — Python · FastAPI · PostgreSQL · Redis · Docker

---

## Requisitos

- Docker Engine 24+
- Docker Compose v2

---

## Subir o projeto

```bash
# 1. Clone / extraia o projeto e entre na pasta
cd lea-record-shop

# 2. Suba todos os containers (API, worker, Postgres, Redis, Frontend)
docker compose up --build -d

# 3. Aguarde ~15s para a API inicializar, depois rode o seed
docker compose exec api python seed.py
```

| Serviço   | URL                              |
|-----------|----------------------------------|
| Frontend  | http://localhost:3000            |
| API       | http://localhost:8000            |
| Swagger   | http://localhost:8000/docs       |
| Postgres  | localhost:5433                   |
| Redis     | localhost:6379                   |

---

## Simular o lançamento (500 discos · 50 req/s)

```bash
# Instalar o hey (load tester)
brew install hey          # macOS
# ou: go install github.com/rakyll/hey@latest

# Disparar 500 requisições com concorrência 50 (equivale a ~50 req/s)
hey -n 500 -c 50 -m POST \
  -H 'Content-Type: application/json' \
  -d '{"cliente_id":1,"itens":[{"disco_id":1,"quantidade":1}]}' \
  http://localhost:8000/pedidos

# Verificar: devem existir exatamente 500 COMPLETED e 0 overselling
curl "http://localhost:8000/pedidos?status=COMPLETED&page_size=1"
curl "http://localhost:8000/pedidos?status=FAILED&page_size=1"
```

### Escalar workers para o lançamento

```bash
docker compose up --scale worker=4 -d
```

---

## Monitorar Redis em tempo real

```bash
# Ver tamanho da fila
docker exec lea_redis redis-cli LLEN pedidos:queue

# Ver estoque do disco 1 (We Are Reactive)
docker exec lea_redis redis-cli GET estoque:1

# Ver todas as chaves
docker exec lea_redis redis-cli KEYS "*"
```

---

## Estrutura do projeto

```
lea-record-shop/
├── app/
│   ├── core/          # config.py, database.py
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── repositories/  # Acesso ao banco
│   ├── services/      # Regras de negócio + Redis
│   ├── controllers/   # FastAPI routers
│   ├── infra/         # Redis connection pool
│   └── worker/        # Consumer da fila (processo separado)
├── frontend/
│   ├── index.html     # SPA completa (login, catálogo, clientes, pedidos)
│   └── Dockerfile
├── seed.py            # Popula banco + Redis com dados de exemplo
├── docker-compose.yml
├── Dockerfile         # Imagem da API
└── Dockerfile.worker  # Imagem do worker
```

---

## Endpoints

### Discos
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/discos` | Lista com filtros (nome, artista, estilo, ano) + paginação |
| GET | `/discos/{id}` | Detalhe |
| POST | `/discos` | Criar |
| PUT | `/discos/{id}` | Atualizar |
| DELETE | `/discos/{id}` | Soft delete |

### Clientes
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/clientes` | Listar |
| POST | `/clientes` | Cadastrar |
| PUT | `/clientes/{id}` | Atualizar |
| PATCH | `/clientes/{id}/inativar` | Inativar (soft delete) |

### Pedidos
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/pedidos` | Enfileirar pedido → 202 PENDING |
| GET | `/pedidos/{id}` | Consultar status |
| GET | `/pedidos` | Listar com filtros (cliente_id, data_inicio, data_fim) |

---

## Arquitetura de concorrência

```
POST /pedidos (~5ms)
  └─ LPUSH pedidos:queue {id}  ← enfileira e retorna imediatamente

Worker (processo separado)
  └─ BRPOP pedidos:queue
       └─ DECRBY estoque:{disco_id} N  ← atômico, sem race condition
            ├─ resultado >= 0 → COMPLETED + persiste no banco
            └─ resultado <  0 → INCRBY rollback + FAILED
```

Consulte `RELATORIO_TECNICO.md` para documentação completa.
