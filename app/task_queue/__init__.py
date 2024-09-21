"""Package for managing the task queue

This rudimentary task queue consists of a Broker, a Worker, and a TaskStore:

Broker -> TaskStore <- Worker

- The Broker, running on the main application thread, receives job
    requests and adds them to the store. It also mediates requests
    for job status and getting the processed result of a job.

- The Worker, running on a separate thread, queries the TaskStore
    for a new task, and when one is available, processes the task
    and registers the result back to the store.

- The TaskStore stores the job requests and processed results. Because
    it obfuscates the internals of how this is done via an interface, any
    storage implementation can be used. The default for this application
    is FileSystemTaskStore, which saves the job request and results to
    the filesystem.
"""

from typing import BinaryIO, Callable

from PIL.Image import Image

from app import settings
from app.task_queue.task_broker import Broker as Broker
from app.task_queue.task_store import FileSystemTaskStore
from app.task_queue.task_store import TaskStatus as TaskStatus
from app.task_queue.worker import Worker as Worker

# Global filesystem task store
task_store = FileSystemTaskStore(settings.task_queue_data_folder)


def get_broker() -> Broker:
    """
    Get a Broker using the TaskStore implementation
    provided by global settings. This behaves like
    a singleton.

    If you need a Broker, this is probably what you want.

    :return: Broker instance
    """
    return Broker(task_store)


def create_worker(task_func: Callable[[BinaryIO], Image]) -> Worker:
    """
    Create a Worker using the TaskStore implementation provided
    by global settings. This behaves like a singleton.

    The application creates workers automatically as needed, so
    you probably won't need to use this.

    :param task_func: Callable the worker will use to process a task.
    :return: Worker instance
    """
    return Worker(task_store, task_func)
