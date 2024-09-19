import pytest

from app.exceptions import JobNotFound
from tests.exceptions import InvalidJobID
from tests.specifications.adapters.adapters import CheckJobStatusAdapter
from tests.specifications.adapters.http_test_client import HTTPTestDriver
from tests.specifications.check_job_status import (
    check_job_status_complete_specification,
    check_job_status_error_specification,
    check_job_status_incomplete_specification,
)


class TestCheckJobStatus:
    def test_check_job_status_complete(self, job_id_complete: str) -> None:
        check_job_status_complete_specification(
            CheckJobStatusAdapter(), job_id_complete
        )

    def test_check_job_status_incomplete(self, job_id_incomplete: str) -> None:
        check_job_status_incomplete_specification(
            CheckJobStatusAdapter(), job_id_incomplete
        )

    def test_check_job_status_error(self, job_id_error: str) -> None:
        check_job_status_error_specification(CheckJobStatusAdapter(), job_id_error)

    def test_check_job_status_not_found(self, job_id_not_found: str) -> None:
        with pytest.raises(JobNotFound):
            check_job_status_complete_specification(CheckJobStatusAdapter(), job_id_not_found)


class TestCheckJobStatusHTTP:

    def test_check_job_status_complete(self, job_id_complete: str) -> None:
        check_job_status_complete_specification(HTTPTestDriver(), job_id_complete)

    def test_check_job_status_incomplete(self, job_id_incomplete: str) -> None:
        check_job_status_incomplete_specification(HTTPTestDriver(), job_id_incomplete)

    def test_check_job_status_error(self, job_id_error: str) -> None:
        check_job_status_error_specification(HTTPTestDriver(), job_id_error)

    def test_check_job_status_invalid_id(self, job_id_invalid: str) -> None:
        with pytest.raises(InvalidJobID):
            check_job_status_complete_specification(HTTPTestDriver(), job_id_invalid)

    def test_check_job_status_not_found(self, job_id_not_found: str) -> None:
        with pytest.raises(JobNotFound):
            check_job_status_complete_specification(HTTPTestDriver(), job_id_not_found)
