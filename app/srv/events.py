import logging
from asyncio import CancelledError, TimeoutError, create_task, wait_for
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.srv.worker_monitor import worker_monitor

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Lifecycle start: launching task queue worker monitor")
    task = create_task(worker_monitor())
    yield
    logger.info("Lifecycle end: shutting down task queue worker monitor")
    task.cancel()
    try:
        await wait_for(task, timeout=5)
    except CancelledError:
        logger.info("Worker monitor shutdown gracefully")
    except TimeoutError:
        logger.warning(
            "Timed out waiting for task queue worker monitor to confirm cancellation, forcing shutdown..."
        )
