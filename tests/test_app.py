"""Collection of acceptance tests."""

from time import sleep
from typing import BinaryIO

import pytest
from docker.models.containers import Container

from app.exceptions import InvalidImage, JobNotFound
from app.task_queue.task_store import TaskStatus
from tests.conftest import square_image
from tests.exceptions import ImageTooLarge, InvalidJobID, MissingContentLength
from tests.specifications.adapters.http_driver import (
    CheckJobStatusHTTPDriver,
    UploadImageHTTPDriver,
)
from tests.specifications.upload_image import (
    upload_image_specification,
    upload_invalid_image_specification,
)


@pytest.mark.slow
@pytest.mark.acceptance
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
    upload_image_http_driver = UploadImageHTTPDriver()
    check_job_status_http_driver = CheckJobStatusHTTPDriver()

    # Upload image happy path. Capture the job id
    job_id = upload_image_specification(upload_image_http_driver)

    # Upload image unhappy paths
    with pytest.raises(InvalidImage):
        upload_invalid_image_specification(upload_image_http_driver)
    with pytest.raises(ImageTooLarge):
        upload_image_http_driver.upload(size_too_large_image)
    with pytest.raises(MissingContentLength):
        upload_image_http_driver.upload_no_content_length(square_image)

    # Check job status happy path.
    status: TaskStatus = TaskStatus.PROCESSING
    resource_url: str | None = None
    counter = 0
    while status != TaskStatus.SUCCEEDED:
        status, resource_url = check_job_status_http_driver.check_job_status(job_id)
        sleep(1)
        counter += 1
        if counter > 10:
            raise TimeoutError("timed out waiting for job to finish processing")

    # Check job status unhappy paths
    with pytest.raises(JobNotFound):
        check_job_status_http_driver.check_job_status(job_id_not_found)
    with pytest.raises(InvalidJobID):
        check_job_status_http_driver.check_job_status(job_id_invalid)

    # ViewAllJobsSpecification()
    # DownloadThumbnailSpecification()
