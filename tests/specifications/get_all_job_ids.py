from typing import Protocol

from tests.task_queue.stubbed_task_store import StubbedTaskStoreBroker


class GetAllJobIds(Protocol):
    def get_all_job_ids(self) -> list[str]: ...


def get_all_job_ids_specification(fetcher: GetAllJobIds) -> None:
    result = fetcher.get_all_job_ids()
    assert StubbedTaskStoreBroker.JobID.COMPLETE in result
    assert StubbedTaskStoreBroker.JobID.INCOMPLETE in result
    assert StubbedTaskStoreBroker.JobID.ERROR in result
