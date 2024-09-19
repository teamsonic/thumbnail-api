import logging
from asyncio import CancelledError, TimeoutError, sleep, to_thread, wait_for

from app.task_queue import create_worker

logger = logging.getLogger(__name__)


async def worker_monitor() -> None:
    logger.info("Starting worker monitor")
    worker = create_worker()
    worker.start()
    try:
        while True:
            try:
                if not worker.is_alive():
                    logger.warning("Worker process no longer alive, restarting")
                    worker = create_worker()
                    worker.start()
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
