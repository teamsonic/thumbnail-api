"""Collection of acceptance and end-to-end tests"""

from time import sleep
from typing import BinaryIO

import pytest
from docker.models.containers import Container
from fastapi import status
from pytest import FixtureRequest

from app import settings
from app.srv import AllJobsModel, Routes, UploadImageModel
from tests.conftest import ACCEPTANCE_TEST_ARTIFACTS_PATH, square_image
from tests.specifications.adapters.http_client_driver import HTTPClientDriver


@pytest.mark.slow
@pytest.mark.acceptance
@pytest.mark.e2e
@pytest.mark.usefixtures("app_docker_container")
class TestServer:
    """
    Test the application behavior end-to-end and verify
    the client-server interactions work in a live setting.

    The order of test methods in this class matter, as subsequent methods
    expect state provided by those than came before.
    """

    job_ids: list[str]

    @classmethod
    def setup_class(cls) -> None:
        # Data that should be persisted during the scope of the class tests.
        # As requests are made to the server to create thumbnails, the
        # corresponding job IDs will be added here.
        cls.job_ids = []

    @pytest.mark.parametrize("route", [Routes.HEALTHCHECK, Routes.DOCS, "/"])
    def test_endpoints(self, route: str) -> None:
        """Test endpoints that aren't interacted with during specification driven tests
        """
        http_client_driver = HTTPClientDriver()

        response = http_client_driver.do_request('GET', route)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize("image", ["square_image", "tall_image", "wide_image", "webp_image", "png_image"])
    def test_thumbnail_creation_end_to_end(
        self, image: str, request: FixtureRequest
    ) -> None:
        """Test the application behavior end-to-end.

        These tests are performed against a running instance of the
        application and use an HTTP driver to assert the system
        specifications via an HTTP interface.

        :param image: Name of pytest fixture that returns an image.
        :param request: pytest fixture that allows requesting other fixtures
            by name instead of by DI. This is done to enable parametrizing.
        """
        http_client_driver = HTTPClientDriver()

        # Get the image from the fixture.
        image_fixture = request.getfixturevalue(image)
        # Upload the image. Make sure it succeeded. The image should now be processing.
        response = http_client_driver.do_request(
            "POST", Routes.UPLOAD_IMAGE, image_fixture
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        # Get the next request URL from the Location header
        next_url = response.headers["Location"]
        # Validate the response
        upload_model = UploadImageModel.model_validate(response.json())
        # Store the job_id for later
        job_id = upload_model.job_id
        self.__class__.job_ids.append(job_id)

        # Using the URL from the Location header, request the task status.
        # As requesting the results of a successful task will return a 303,
        # repeat this request until the thumbnail data is returned. If this takes
        # longer than 5 seconds, fail the test.
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

        # Write out the thumbnail to a file. You can manually inspect it to make
        # sure it looks good!
        assert response.status_code == status.HTTP_200_OK
        with open(f"{ACCEPTANCE_TEST_ARTIFACTS_PATH}/{image}.jpg", "wb") as f:
            f.write(response.content)

    def test_get_all_jobs(self) -> None:
        """Test the endpoint that returns all jobs.

        This is meant to be executed immediately after test_server() for
        best results, as there will be tasks in the application to return.

        Otherwise, you'll just be asserting empty lists are equal.
        """
        http_client_driver = HTTPClientDriver()
        response = http_client_driver.do_request("GET", Routes.JOBS)
        assert response.status_code == status.HTTP_200_OK
        all_jobs_model = AllJobsModel.model_validate(response.json())
        assert len(all_jobs_model.job_ids) == len(self.__class__.job_ids)
        assert set(all_jobs_model.job_ids) == set(self.__class__.job_ids)

    def test_upload_rejected_for_missing_content_length(
        self, square_image: BinaryIO
    ) -> None:
        """Upload requests should be rejected for missing content-length header.

        :param square_image: Just some image. You can use anything for this test.
        """
        http_client_driver = HTTPClientDriver()
        session, prepared = http_client_driver.make_request(
            "POST", Routes.UPLOAD_IMAGE, files={"file": square_image}
        )
        del prepared.headers["content-length"]
        response = session.send(prepared)
        assert response.status_code == status.HTTP_411_LENGTH_REQUIRED
