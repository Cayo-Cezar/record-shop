"""
pedido_worker.py
================
Standalone consumer process. Run as a separate container or process.

Flow:
  BRPOP pedidos:queue (blocks up to WORKER_BRPOP_TIMEOUT seconds)
  → load pedido from DB
  → DECRBY stock atomically in Redis (one op per item)
  → if any item goes negative → INCRBY rollback → mark FAILED
  → if all ok → sync to DB → mark COMPLETED

To run:
    python -m app.worker.pedido_worker
"""

import signal
import sys
import logging
import time

from app.core.database import SessionLocal
from app.core.config import settings
from app.infra.redis_client import get_redis
from app.services.pedido_service import pedido_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WORKER] %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

# Graceful shutdown flag
_running = True


def _handle_signal(sig, frame):
    global _running
    log.info("Shutdown signal received — finishing current job then stopping.")
    _running = False


signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


def run() -> None:
    r = get_redis()
    log.info(
        "Worker started. Listening on queue '%s' …", settings.PEDIDO_QUEUE_KEY
    )

    consecutive_errors = 0
    MAX_CONSECUTIVE_ERRORS = 10

    while _running:
        try:
            # BRPOP blocks for up to WORKER_BRPOP_TIMEOUT seconds then returns None
            result = r.brpop(settings.PEDIDO_QUEUE_KEY, timeout=settings.WORKER_BRPOP_TIMEOUT)

            if result is None:
                # Timeout — loop and check _running again
                continue

            _, raw_pedido_id = result
            pedido_id = int(raw_pedido_id)
            log.info("Picked up pedido_id=%s", pedido_id)

            db = SessionLocal()
            try:
                pedido_service.process_stock(db, pedido_id)
                log.info("pedido_id=%s processed successfully", pedido_id)
                consecutive_errors = 0
            except Exception as exc:
                log.error("Error processing pedido_id=%s: %s", pedido_id, exc, exc_info=True)
                # Push to dead-letter queue for manual inspection
                r.lpush(settings.PEDIDO_DEAD_QUEUE_KEY, pedido_id)
                consecutive_errors += 1
            finally:
                db.close()

            # Circuit-breaker: if too many consecutive errors, pause briefly
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                log.warning(
                    "Too many consecutive errors (%s). Pausing 5s …", consecutive_errors
                )
                time.sleep(5)
                consecutive_errors = 0

        except Exception as exc:
            log.critical("Unexpected worker loop error: %s", exc, exc_info=True)
            time.sleep(2)

    log.info("Worker stopped cleanly.")


if __name__ == "__main__":
    run()
