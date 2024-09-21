"""Assert interaction to get all job ids"""

from tests.specifications.adapters.adapters import GetAllJobIdsAdapter
from tests.specifications.adapters.http_test_driver import HTTPTestDriver
from tests.specifications.get_all_job_ids import get_all_job_ids_specification


class TestGetAllJobIds:
    """
    Drive the specification for getting all job ids directly
    without any interface. Unit tests.
    """

    def test_get_all_job_ids(self) -> None:
        get_all_job_ids_specification(GetAllJobIdsAdapter())


class TestGetAllJobIdsHTTP:
    """
    Drive the specification for getting all job ids
    via an HTTP interface.
    """

    def test_get_all_job_ids_http(self) -> None:
        get_all_job_ids_specification(HTTPTestDriver())
