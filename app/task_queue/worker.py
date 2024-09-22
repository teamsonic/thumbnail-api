import logging
import threading
from time import sleep
from typing import BinaryIO, Callable

from PIL import Image, UnidentifiedImageError

from app import settings
from app.exceptions import InvalidImage
from app.task_queue.task_store import TaskStoreWorker

logger = logging.getLogger(__name__)


class Worker(threading.Thread):
    """Worker thread for processing tasks separately from the main application.

    As it subclasses the Thread class, Worker can be started just like a thread:
        >>> worker = Worker(..., ...)
        >>> worker.start()
    which will do some special Thread stuff and eventually call run(), which
    defines the worker loop of requesting a task from the task store, running
    the task through a task function, and submitting the results back to the
    task store.

    Methods:
    -------
    start(self) -> None: Call this to start the thread. It can only be called once.
    run(self) -> None: Called automatically by start() and is the worker loop.
    interrupt(self) -> None: Send a request to the worker to stop working. Unless
        it is forcibly killed, it will finish its current task before shutting down.
    """

    def __init__(
        self, task_store: TaskStoreWorker, task_func: Callable[[BinaryIO], Image.Image]
    ) -> None:
        super().__init__()
        self.name = f"Worker {self.name}"
        self._task_store = task_store
        self._task_func = task_func
        self.interrupted = False

    def interrupt(self) -> None:
        """Send a request to the worker to stop working.

        The worker is not guaranteed to shut down immediately after
        receiving an interrupt signal, as it may be in the middle of a task.
        If you want to block until the worker has shut down, use Thread.join()
        """
        self.interrupted = True

    def _get_task(self) -> tuple[str, BinaryIO] | None:
        """Get the next task from the task store.

        :return: The job id and image data of the task, or None if there are no tasks
        """
        return self._task_store.get_next_task()

    def _do_task(self, job_id: str, image: BinaryIO) -> None:
        """Process the image and register the result with the task store.

        If there is an Exception, it will be caught and error message
        will be sent to the task store to be returned to the user
        when they request their job status.

        :param job_id: Unique ID of the job being processed
        :param image: Binary image data to be converted to a thumbnail
        """
        err: Exception | None = None
        message: str | None = None

        try:
            thumbnail = self._task_func(image)
            return self._task_store.register_task_complete(
                job_id, thumbnail, settings.thumbnail_file_type
            )
        except UnidentifiedImageError as e:
            err = e
            message = "File could not be identified as an image"
        except Exception as e:
            err = e
            message = "There was an error converting your file to a thumbnail."

        self._task_store.register_task_error(job_id, message)
        raise err

    def run(self) -> None:
        """Worker logic. This is the loop the worker runs after starting.

        Don't call this directly, use start() instead.

        The worker will ask the task store for a task, do the task, then
        submit the results back to the task store. If there is an error
        during processing, it will submit an error result to the task store.
        If there are no tasks available, it will sleep, then ask again later.
        As all Exceptions are caught, this loop will run indefinitely unless
        even if encountering Exceptions.

        Calling interrupt() will request the worker shutdown, which
        it will do immediately after finishing the task it is processing.
        """
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
                logger.exception(e, exc_info=True)

        self.interrupted = False
        logger.info("Thread interrupted -- shutting down")
