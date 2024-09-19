import logging
import threading
from time import sleep
from typing import BinaryIO

import PIL

from app.domain.create_thumbnail import create_thumbnail
from app.exceptions import InvalidImage
from app.task_queue.task_store import TaskStoreWorker

logger = logging.getLogger(__name__)


class Worker(threading.Thread):
    def __init__(self, task_store: TaskStoreWorker) -> None:
        super().__init__()
        self._task_store = task_store
        self.interrupted = False

    def interrupt(self) -> None:
        self.interrupted = True

    def _get_task(self) -> tuple[str, BinaryIO] | None:
        return self._task_store.get_next_task()

    def _do_task(self, job_id: str, image: BinaryIO) -> None:
        err: Exception | None = None

        try:
            thumbnail = create_thumbnail(image)
        except PIL.UnidentifiedImageError:
            err = InvalidImage("file could not be identified as an image")
        except Exception as e:
            err = e
        else:
            return self._task_store.register_task_complete(job_id, thumbnail)

        logger.exception(err)
        self._task_store.register_task_error(job_id, err)

    def run(self) -> None:
        logger.info(f"Worker thread {self.name} starting up")

        while not self.interrupted:
            try:
                logger.debug("Looking for next task")
                task = self._get_task()
                if not task:
                    logger.debug("No new tasks available. Sleeping...")
                    sleep(1)
                    continue
                logger.debug(f"Starting task {task[0]}")
                self._do_task(*task)
                logger.debug(f"Finished task {task[0]}")
            except Exception as e:
                logger.exception(e)

        self.interrupted = False
        logger.info("Thread interrupted -- shutting down")
