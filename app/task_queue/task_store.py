"""Module defining TaskStore Protocols and their implementations.

Exports:
-------
TaskStatus - Enum of possible states a task can be in
TaskStoreBroker - Protocol defining methods needed for a TaskStore
    to communicate with a Broker.
TaskStoreWorker - Protocol defining methods needed for a TaskStore
    to communicate with a Worker.
FileSystemTaskStore - Concrete class using the filesystem for task state
    implementing both TaskStoreBroker and TaskStoreWorker.
"""

import io
import os
import shutil
import uuid
from enum import StrEnum
from pathlib import Path
from typing import BinaryIO, Iterable, Protocol

from PIL import Image

from app.exceptions import JobNotFound


class TaskStatus(StrEnum):
    """Enum of all possible task states."""

    PROCESSING = "Processing"
    SUCCEEDED = "Succeeded"
    ERROR = "Error"
    NOT_FOUND = "Not Found"


class TaskStoreBroker(Protocol):
    """Protocol for a TaskStore to be able to communicate with a Broker."""

    def add_task_to_queue(self, image: BinaryIO) -> str: ...

    def get_task_status(self, job_id: str) -> TaskStatus: ...

    def get_all_task_status(self) -> dict[TaskStatus, Iterable[str]]: ...

    def get_result(self, job_id: str) -> BinaryIO: ...

    def get_error(self, job_id: str) -> str: ...


class TaskStoreWorker(Protocol):
    """Protocol for a TaskStore to be able to communicate with a Worker."""

    def get_next_task(self) -> tuple[str, BinaryIO] | None: ...

    def register_task_complete(
        self, job_id: str, thumbnail: Image.Image, image_format: str
    ) -> None: ...

    def register_task_error(self, job_id: str, error: Exception) -> None: ...


class FileSystemTaskStore(TaskStoreBroker, TaskStoreWorker):
    """TaskStore using the filesystem that can communicate with both Brokers and Workers

    When this class is initialized, it ensures that all folders it needs are present
    on the filesystem. The root folder is provided during initialization.

    This class is not thread safe and unexpected results may occur if used
    by more than one Worker at a time.

    A TaskStore only does three main things:
    - Serialize and store new task requests from a Broker.
    - Store results of completed tasks from a Worker.
    - Report on task status if requested by a Broker.

    Methods:
    -------
    reset(self) -> None: Reinitialize the TaskStore. This deletes all tasks.
    add_task_to_queue(self, image: BinaryIO) -> str: Create a task to process an image
        and return the ID of the task.
    get_task_status(self, job_id: str) -> TaskStatus: Get the task status of a job.
    get_all_task_status(self) -> dict[TaskStatus, Iterable[str]]: Get the task status
        of all jobs.
    get_result(self, job_id: str) -> BinaryIO: Get the result of a completed task.
    get_error(self, job_id: str) -> str: Get the error message from a failed task.
    get_next_task(self) -> tuple[str, BinaryIO] | None: Return an unstarted task.
        If there are multiple unstarted tasks, the order in which they are
        returned is undefined.
    register_task_complete(self, job_id: str, thumbnail: Image.Image,
        image_format: str) -> None:
        Used by workers to submit the results of a completed task.
    register_task_error(self, job_id: str, error: Exception) -> None:
        Used by workers to submit the results of a failed task.
    """

    _in_folder = "in"
    _out_folder = "out"
    _error_folder = "error"

    def __init__(self, data_folder: str) -> None:
        """
        Initialize the file store by ensuring that all necessary folders
        exist.

        :param data_folder: Root path of the file store.
        """
        self._root = Path(data_folder)
        self._init_folders()

    def _init_folders(self) -> None:
        self._root.mkdir(exist_ok=True)
        self._folders: dict[str, Path] = {}

        for folder in [self._in_folder, self._out_folder, self._error_folder]:
            path = self._root.joinpath(folder)
            path.mkdir(exist_ok=True)
            self._folders[folder] = path

    def reset(self) -> None:
        """Reinitialize the TaskStore. This deletes all tasks."""
        shutil.rmtree(self._root, ignore_errors=True)
        self._init_folders()

    @property
    def in_folder(self) -> Path:
        return self._folders["in"]

    @property
    def out_folder(self) -> Path:
        return self._folders["out"]

    @property
    def error_folder(self) -> Path:
        return self._folders["error"]

    def _in_job_path(self, job_id: str) -> Path:
        return self.in_folder.joinpath(job_id)

    def _out_job_path(self, job_id: str) -> Path:
        return self.out_folder.joinpath(job_id)

    def _error_job_path(self, job_id: str) -> Path:
        return self.error_folder.joinpath(job_id)

    def _job_is_processing(self, job_id: str) -> bool:
        return self._in_job_path(job_id).exists()

    def _job_is_finished(self, job_id: str) -> bool:
        return self._out_job_path(job_id).exists()

    def _job_is_error(self, job_id: str) -> bool:
        return self._error_job_path(job_id).exists()

    def _job_ids_with_status(self, task_status: TaskStatus) -> Iterable[str]:
        """Find all jobs with provided TaskStatus

        :param task_status: Status to query for
        :return: All tasks meeting the TaskStatus query
        """
        folder: Path
        if task_status == TaskStatus.PROCESSING:
            folder = self.in_folder
        elif task_status == TaskStatus.SUCCEEDED:
            folder = self.out_folder
        elif task_status == TaskStatus.ERROR:
            folder = self.error_folder
        else:
            raise Exception(f"Unknown task status: {task_status}")
        return os.listdir(folder)

    def add_task_to_queue(self, image: BinaryIO) -> str:
        """Create a task to process an image and return the ID of the task.

        :param image: File data of image to be processed
        :return: A uuid-compliant string uniquely identifying the task.
        """
        job_id = str(uuid.uuid4())
        self._in_job_path(job_id).write_bytes(image.read())
        return job_id

    def get_task_status(self, job_id: str) -> TaskStatus:
        """Get the task status of a job.

        :param job_id: The ID uniquely identifying a task
        :return: The TaskStatus of the task.
        """
        if self._job_is_finished(job_id):
            return TaskStatus.SUCCEEDED
        elif self._job_is_processing(job_id):
            return TaskStatus.PROCESSING
        elif self._job_is_error(job_id):
            return TaskStatus.ERROR
        else:
            return TaskStatus.NOT_FOUND

    def get_all_task_status(self) -> dict[TaskStatus, Iterable[str]]:
        """Get the task status of all tasks, grouped by status.

        :return: A dictionary whose keys are the unique statuses and the
            values are the job IDs with that status.
        """
        return {
            TaskStatus.PROCESSING: self._job_ids_with_status(TaskStatus.PROCESSING),
            TaskStatus.SUCCEEDED: self._job_ids_with_status(TaskStatus.SUCCEEDED),
            TaskStatus.ERROR: self._job_ids_with_status(TaskStatus.ERROR),
        }

    def get_result(self, job_id: str) -> BinaryIO:
        """Get the result of a completed task.

        :param job_id: The ID uniquely identifying a task
        :return: The results of the completed task.
        :raises: JobNotFound if no completed job is found with the given ID.
        """
        if self._job_is_finished(job_id):
            return io.BytesIO(self.out_folder.joinpath(job_id).read_bytes())
        raise JobNotFound(f"No completed job found with ID {job_id}")

    def get_error(self, job_id: str) -> str:
        """Get the error message from a failed task.

        :param job_id: The ID uniquely identifying a task.
        :return: The error message from a failed task.
        :raises: JobNotFound if no failed job is found with the given ID.
        """
        if not self._job_is_error(job_id):
            raise JobNotFound(f"No error job found with ID {job_id}")
        return self._error_job_path(job_id).read_text("utf-8")

    def get_next_task(self) -> tuple[str, BinaryIO] | None:
        """Return an unstarted task.

        The order in which unstarted tasks are returned is undefined, making
        this not strictly a queue.

        A clear danger of this method is that the task is deleted after
        being loaded into memory and before delivering it to a worker.
        Not only is there a danger of the worker crashing before submitting
        the results, which would cause the task to be lost completely, but
        any queries for task status during this period would return
        TaskStatus.NOT_FOUND, which would be misleading.

        :return: An unstarted task, or None, if there are no tasks to be done.
        """
        tasks = self._job_ids_with_status(TaskStatus.PROCESSING)
        try:
            job_id = next(iter(tasks))
        except StopIteration:
            return None

        image_path = self._in_job_path(job_id)
        image_data = io.BytesIO(image_path.read_bytes())
        os.remove(image_path)
        return job_id, image_data

    def register_task_complete(
        self, job_id: str, thumbnail: Image.Image, image_format: str
    ) -> None:
        """Register the completed results of a task.

        :param job_id: ID uniquely identifying a task.
        :param thumbnail: The thumbnail created by the worker.
        :param image_format: The image format of the thumbnail.
        """
        thumbnail_path = self._out_job_path(job_id)
        thumbnail.save(thumbnail_path, format=image_format)

    def register_task_error(self, job_id: str, error: Exception) -> None:
        """Register the error message from a failed task.

        :param job_id: ID uniquely identifying a task.
        :param error: The error that occurred during thumbnail generation.
        """
        error_path = self._error_job_path(job_id)
        error_path.write_text(str(error), "utf-8")
