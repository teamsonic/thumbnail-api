"""Collection of acceptance tests."""

from time import sleep
from typing import BinaryIO

import pytest
from docker.models.containers import Container
from fastapi import status

from app.srv.models import JobStatusModel, UploadImageModel, AllJobs
from app.task_queue.task_store import TaskStatus
from tests.conftest import square_image
from tests.specifications.adapters.http_driver import HTTPClientDriver


@pytest.mark.slow
@pytest.mark.acceptance
@pytest.mark.e2e
def test_server(
    app_docker_container: Container,
    square_image: BinaryIO,
    size_too_large_image: BinaryIO,
    job_id_not_found: str,
    job_id_invalid: str,
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
    response = http_client_driver.do_request("POST", "/upload_image", square_image)
    assert response.status_code == status.HTTP_202_ACCEPTED
    upload_model = UploadImageModel.model_validate(response.json())
    job_id = upload_model.job_id

    session, prepared = http_client_driver.make_request(
        "POST", "/upload_image", files={"file": square_image}
    )
    del prepared.headers["content-length"]
    response = session.send(prepared)
    assert response.status_code == status.HTTP_411_LENGTH_REQUIRED

    task_status: TaskStatus = TaskStatus.PROCESSING
    counter = 0
    while task_status != TaskStatus.SUCCEEDED:
        response = http_client_driver.do_request("GET", f"/check_job_status/{job_id}")
        assert response.status_code == status.HTTP_200_OK
        job_status_model = JobStatusModel.model_validate(response.json())
        task_status = job_status_model.status
        sleep(1)
        counter += 1
        if counter > 10:
            raise TimeoutError("timed out waiting for job to finish processing")

    response = http_client_driver.do_request("GET", "/jobs")
    assert response.status_code == status.HTTP_200_OK
    all_jobs_model = AllJobs.model_validate(response.json())
    assert len(all_jobs_model.job_ids) == 1
    assert all_jobs_model.job_ids[0] == job_id
    # DownloadThumbnailSpecification()
