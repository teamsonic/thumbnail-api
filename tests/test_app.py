"""Collection of acceptance tests."""

from time import sleep
from typing import BinaryIO

import pytest
from docker.models.containers import Container
from fastapi import status
from pytest import FixtureRequest

from app import settings
from app.srv.models import AllJobs, UploadImageModel
from app.srv.routes import Routes
from tests.conftest import ACCEPTANCE_TEST_ARTIFACTS_PATH, square_image
from tests.specifications.adapters.http_client_driver import HTTPClientDriver


@pytest.mark.slow
@pytest.mark.acceptance
@pytest.mark.e2e
class TestServer:
    job_ids: list[str]

    @classmethod
    def setup_class(cls) -> None:
        cls.job_ids = []

    @pytest.mark.parametrize("image", ["square_image", "tall_image", "wide_image"])
    def test_server(
        self, app_docker_container: Container, image: str, request: FixtureRequest
    ) -> None:
        """Test the application behavior end-to-end.

        These tests are performed against a running instance of the
        application and use an HTTP driver to assert the system
        specifications via an HTTP interface.

        :param app_docker_container: docker container running this application
        :param square_image: image of an acceptable size to test happy path
        :param size_too_large_image: image that should be rejected for being too big
        """
        http_client_driver = HTTPClientDriver()
        image_fixture = request.getfixturevalue(image)

        response = http_client_driver.do_request(
            "POST", Routes.UPLOAD_IMAGE, image_fixture
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        next_url = response.headers["Location"]
        upload_model = UploadImageModel.model_validate(response.json())
        job_id = upload_model.job_id
        self.__class__.job_ids.append(job_id)

        counter = 0
        while True:
            response = http_client_driver.do_request("GET", next_url)
            content_type = response.headers["content-type"]
            if content_type.lower() == f"image/{settings.thumbnail_file_type}".lower():
                break
            sleep(1)
            counter += 1
            if counter > 5:
                raise TimeoutError("timed out waiting for job to finish processing")

        assert response.status_code == status.HTTP_200_OK
        with open(f"{ACCEPTANCE_TEST_ARTIFACTS_PATH}/{image}.jpg", "wb") as f:
            f.write(response.content)

    def test_get_all_jobs(self) -> None:
        http_client_driver = HTTPClientDriver()
        response = http_client_driver.do_request("GET", Routes.JOBS)
        assert response.status_code == status.HTTP_200_OK
        all_jobs_model = AllJobs.model_validate(response.json())
        assert len(all_jobs_model.job_ids) == len(self.__class__.job_ids)
        assert set(all_jobs_model.job_ids) == set(self.__class__.job_ids)

    def test_upload_rejected_for_missing_content_length(
        self, square_image: BinaryIO
    ) -> None:
        http_client_driver = HTTPClientDriver()
        session, prepared = http_client_driver.make_request(
            "POST", Routes.UPLOAD_IMAGE, files={"file": square_image}
        )
        del prepared.headers["content-length"]
        response = session.send(prepared)
        assert response.status_code == status.HTTP_411_LENGTH_REQUIRED
