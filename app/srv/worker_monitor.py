import logging
from asyncio import CancelledError, TimeoutError, sleep, to_thread, wait_for

from app.domain import create_thumbnail
from app.task_queue import create_worker
from app.task_queue.worker import Worker

logger = logging.getLogger(__name__)


async def worker_monitor() -> None:
    """Start and monitor the task queue worker thread

    The worker thread is a mission-critical process
    that watches for thumbnail-creation tasks. If
    the worker is not available, images can still
    be uploaded, but will never be processed into
    thumbnails.

    This worker monitor watches the worker and will
    restart it indefinitely whenever it dies, which
    it never should, but...

    The application will start and stop this monitor
    automatically as part of its startup/shutdown lifecycle.
    """

    def start_worker() -> Worker:
        w = create_worker(create_thumbnail)
        w.start()
        return w

    logger.info("Starting worker monitor")
    worker = start_worker()
    try:
        while True:
            try:
                if not worker.is_alive():
                    logger.warning("Worker process no longer alive, restarting")
                    worker = start_worker()
            except Exception as e:
                logging.exception(e)
            await sleep(1)
    except CancelledError:
        logger.info(
            "Worker monitor received cancellation signal, requesting worker to shutdown"
        )
        raise
    finally:
        worker.interrupt()
        try:
            await wait_for(to_thread(worker.join), timeout=5)
        except TimeoutError:
            logger.warning(
                "Timed out waiting for worker thread to stop, forcing shutdown"
            )
