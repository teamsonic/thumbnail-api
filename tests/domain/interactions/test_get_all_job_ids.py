from tests.specifications.adapters.adapters import GetAllJobIdsAdapter
from tests.specifications.adapters.http_test_client import HTTPTestDriver
from tests.specifications.get_all_job_ids import get_all_job_ids_specification


def test_get_all_job_ids() -> None:
    get_all_job_ids_specification(GetAllJobIdsAdapter())


def test_get_all_job_ids_http() -> None:
    get_all_job_ids_specification(HTTPTestDriver())
