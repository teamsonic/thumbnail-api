from typing import Protocol

from tests.conftest import JobID


class GetAllJobIds(Protocol):
    def get_all_job_ids(self) -> list[str]: ...


def get_all_job_ids_specification(fetcher: GetAllJobIds) -> None:
    result = fetcher.get_all_job_ids()
    assert JobID.COMPLETE in result
    assert JobID.INCOMPLETE in result
    assert JobID.ERROR in result
