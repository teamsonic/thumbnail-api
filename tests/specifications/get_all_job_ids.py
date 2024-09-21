"""Specifications for what should happen when all job ids are requested."""

from typing import Protocol

from tests.conftest import JobID


class GetAllJobIds(Protocol):
    """
    A protocol describing the interface for getting all job ids.

    "Ask for all job ids, and get a list of job ids back."
    """

    def get_all_job_ids(self) -> list[str]: ...


def get_all_job_ids_specification(fetcher: GetAllJobIds) -> None:
    """Describes the specification of getting all job ids.

    "When all job ids are requested, they are returned."

    Note: This specification is currently expecting its requests
    for job ids to make it to StubbedTaskStore and is asserting
    on the stubbed response.

    :param fetcher: Any object implementing the GetAllJobIds protocol
    """
    result = fetcher.get_all_job_ids()
    assert JobID.COMPLETE in result
    assert JobID.INCOMPLETE in result
    assert JobID.ERROR in result
