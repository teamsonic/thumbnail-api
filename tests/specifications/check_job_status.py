"""Specifications for what should happen when a job status is checked."""

from typing import Protocol

from app.task_queue import TaskStatus


class CheckJobStatus(Protocol):
    """
    A protocol describing the interface for checking the job status.

    "Send a job_id, get its status and an optional message"
    """

    def check_job_status(self, job_id: str) -> tuple[TaskStatus, str | None]: ...


def check_job_status_complete_specification(
    status_checker: CheckJobStatus, job_id: str
) -> None:
    """Describes the specification of checking a job status whose job is finished.

    "When a job status is requested and the job is complete,
    the caller receives the completed status and no message"

    :param status_checker: Any object implementing the CheckJobStatus protocol
    :param job_id: The job id to check
    """
    result = status_checker.check_job_status(job_id)
    assert result[0] == TaskStatus.SUCCEEDED
    assert not result[1]


def check_job_status_incomplete_specification(
    status_checker: CheckJobStatus, job_id: str
) -> None:
    """Describes the specification of checking a job status whose job is incomplete.

    "When a job status is requested and the job is incomplete,
    the caller receives the processing status and no message."

    :param status_checker: Any object implementing the CheckJobStatus protocol
    :param job_id: The job id to check
    """
    response = status_checker.check_job_status(job_id)
    assert response[0] == TaskStatus.PROCESSING
    assert not response[1]


def check_job_status_error_specification(
    status_checker: CheckJobStatus, job_id: str
) -> None:
    """Describes the specification of checking a job that has failed.

    "When a job status is requested and the job has failed,
    the caller receives the error status and an error message."

    :param status_checker: Any object implementing the CheckJobStatus protocol
    :param job_id: The job id to check
    """
    response = status_checker.check_job_status(job_id)
    assert response[0] == TaskStatus.ERROR
    assert response[1]
