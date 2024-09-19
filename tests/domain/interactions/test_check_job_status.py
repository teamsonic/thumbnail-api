from tests.specifications.adapters.adapters import CheckJobStatusAdapter
from tests.specifications.check_job_status import (
    check_job_status_complete_specification,
    check_job_status_error_specification,
    check_job_status_incomplete_specification,
)


def test_check_job_status(
    job_id_complete: str, job_id_incomplete: str, job_id_error: str
) -> None:
    adapter = CheckJobStatusAdapter()
    check_job_status_complete_specification(adapter, job_id_complete)
    check_job_status_incomplete_specification(adapter, job_id_incomplete)
    check_job_status_error_specification(adapter, job_id_error)
