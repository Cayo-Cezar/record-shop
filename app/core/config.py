from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql://user:password@postgres:5432/lea_db"

    REDIS_URL: str = "redis://redis:6379/0"

    DISCO_CACHE_TTL: int = 300      # Individual disco: 5 minutes
    DISCO_LIST_CACHE_TTL: int = 60  # Disco list: 1 minute
    STOCK_KEY_PREFIX: str = "estoque"
    DISCO_CACHE_PREFIX: str = "disco"
    DISCO_LIST_CACHE_PREFIX: str = "discos:list"

    PEDIDO_QUEUE_KEY: str = "pedidos:queue"
    PEDIDO_DEAD_QUEUE_KEY: str = "pedidos:dead"
    WORKER_BRPOP_TIMEOUT: int = 5   # Seconds to block on BRPOP


settings = Settings()
