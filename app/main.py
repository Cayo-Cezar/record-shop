from fastapi import FastAPI
from app.core.database import engine
from app.core.database import engine, Base
import app.models  

app = FastAPI()


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def test_connection():
    try:
        conn = engine.connect()
        print("✅ Banco conectado com sucesso")
        conn.close()
    except Exception as e:
        print("❌ Erro ao conectar:", e)


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/test-db")
def test_db():
    from app.core.database import engine
    
    try:
        conn = engine.connect()
        conn.close()
        return {"db": "ok"}
    except Exception as e:
        return {"db": "erro", "detail": str(e)}
    

from app.core.database import SessionLocal
from app.models import Cliente, Disco, Pedido, ItemPedido

@app.get("/test-models")
def test_models():
    db = SessionLocal()

    cliente = Cliente(nome="Teste", email="teste@email.com")
    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    disco = Disco(titulo="Disco Teste", artista="Artista", preco=50.0, estoque=5)
    db.add(disco)
    db.commit()
    db.refresh(disco)

    pedido = Pedido(cliente_id=cliente.id)
    db.add(pedido)
    db.commit()
    db.refresh(pedido)

    item = ItemPedido(pedido_id=pedido.id, disco_id=disco.id, quantidade=1)
    db.add(item)
    db.commit()

    db.close()

    return {"status": "ok"}