from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base, SessionLocal
import app.models  # noqa: F401 — ensures all models are registered with Base

from app.controllers.disco_controller import router as disco_router
from app.controllers.cliente_controller import router as cliente_router
from app.controllers.pedido_controller import router as pedido_router
from app.controllers.seed_controller import router as seed_router, seed_data_logic
from app.services.disco_service import disco_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ------------------------------------------------------------------
    # Startup
    # ------------------------------------------------------------------
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas / verificadas")

    yield
    # ------------------------------------------------------------------
    # Shutdown (nothing to clean up here — Redis pool closes automatically)
    # ------------------------------------------------------------------


app = FastAPI(
    title="Lea Record Shop API",
    description="API de e-commerce para a loja de discos Lea Record Shop",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(disco_router)
app.include_router(cliente_router)
app.include_router(pedido_router)
app.include_router(seed_router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
