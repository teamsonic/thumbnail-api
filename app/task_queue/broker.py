from typing import BinaryIO, Iterable

from app.task_queue.task_store import TaskStatus, TaskStoreBroker


class Broker:
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
        :return: A tuple with the completed status and a resource_url to fetch the
         results if True. e.g. (True, "https://server.com/...")
        :raises: JobNotFound if there is no task with the given job_id.
        """
        return self._task_store.get_task_status(job_id)

    def get_result(self, job_id: str) -> BinaryIO:
        """Return the result of the task, which is a thumbnail

        :param job_id: ID of the job
        :return: Image file data
        :raises: JobNotFound if there is no completed job with the given ID
        """
        return self._task_store.get_result(job_id)

    def get_error_result(self, job_id: str) -> str:
        """Return the result of the task, which is a thumbnail

        :param job_id: ID of the job
        :return: Error message
        :raises: JobNotFound if there is no error job with the given ID
        """
        return self._task_store.get_error(job_id)

    def get_all_results(self) -> dict[TaskStatus, Iterable[str]]:
        return self._task_store.get_all_task_status()
