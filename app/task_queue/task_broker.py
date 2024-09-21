from typing import BinaryIO, Iterable

from app.task_queue.task_store import TaskStatus, TaskStoreBroker


class Broker:
    """Handles communication to and from a TaskStore.

    In practice, this makes the broker primarily a proxy that forwards
    requests about job status to a TaskStore.

    Methods:
    -------
    add_task(self, image: BinaryIO) -> str: Create a task in the task queue
        to process a thumbnail from an image and return its ID.

    task_status(self, job_id: str) -> TaskStatus: Get the status of a task.

    get_result(self, job_id: str) -> BinaryIO: Get the processed thumbnail
        for this job, if available.

    get_error_result(self, job_id: str) -> str: Get the error details
        of a failed task, if available.

    get_all_results(self) -> dict[TaskStatus, Iterable[str]]: Get status
        for all jobs in the TaskStore, grouped by status.
    """

    def __init__(self, task_store: TaskStoreBroker) -> None:
        self._task_store = task_store

    def add_task(self, image: BinaryIO) -> str:
        """Adds a task to the queue and returns the job_id.

        :param image: The image on which this task should be performed.
        :return: The uuid-compliant job_id as a str
        """
        return self._task_store.add_task_to_queue(image)

    def task_status(self, job_id: str) -> TaskStatus:
        """Return the status of the task by job_id.

        :param job_id: Unique ID of the task to query for status.
        :return: The status of the Job.
        :raises: JobNotFound if there is no task with the given job_id.
        """
        return self._task_store.get_task_status(job_id)

    def get_result(self, job_id: str) -> BinaryIO:
        """Return the processed result of the task.

        :param job_id: ID of the job
        :return: Thumbnail image file data
        :raises: JobNotFound if there is no completed job with the given ID
        """
        return self._task_store.get_result(job_id)

    def get_error_result(self, job_id: str) -> str:
        """Return the error details of a failed task.

        :param job_id: ID of the job
        :return: An error message
        :raises: JobNotFound if there is no error job with the given ID
        """
        return self._task_store.get_error(job_id)

    def get_all_results(self) -> dict[TaskStatus, Iterable[str]]:
        """Get all jobs and associated statuses from the TaskStore.

        :return: Job IDs organized by TaskStatus.
        """
        return self._task_store.get_all_task_status()
