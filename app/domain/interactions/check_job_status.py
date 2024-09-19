from app.exceptions import JobNotFound
from app.task_queue import broker
from app.task_queue.task_store import TaskStatus


def check_job_status(job_id: str) -> tuple[TaskStatus, str | None]:
    """Look up a job with the provided job_id and return its status.

    Along with the TaskStatus, if the job failed, any error message
    associated with the failure that should be displayed to the uploader is returned.

    :param job_id: The uuid of the job
    :return: tuple of TaskStatus and associated error message, if any
    """
    task_status = broker.task_status(job_id)
    message = None

    if task_status == TaskStatus.NOT_FOUND:
        raise JobNotFound(f"Job with {job_id} was not found.")
    if task_status == TaskStatus.ERROR:
        message = broker.get_error_result(job_id)

    return task_status, message
