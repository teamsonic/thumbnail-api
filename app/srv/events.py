"""Lifespan events for FastAPI

See https://fastapi.tiangolo.com/advanced/events/
"""

import logging
from asyncio import CancelledError, TimeoutError, create_task, wait_for
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.srv.worker_monitor import worker_monitor

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator[None, None]:
    """Context manager handling startup and shutdown events

    Everything before the yield statement is executed before the
    application starts, and everything after is executed when
    the application is shutting down.

    On startup:
    - The worker monitor is launched, which watches the task queue worker
        thread and restarts it if it unexpectedly shuts down as it is a
        critical component.

    On shutdown:
    - The worker monitor is sent a cancellation signal and given
        a 5-second grace period is allotted for confirmation before
        forcibly terminating it.

    :param fastapi_app: The FastApi app
    """
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
            "Timed out waiting for task queue worker monitor to confirm cancellation, "
            "forcing shutdown..."
        )
