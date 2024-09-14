import pytest
from docker.models.containers import Container

from app.specifications.adapters.http_driver import HTTPDriver
from app.specifications.upload_image import upload_image_specification


@pytest.mark.slow
@pytest.mark.acceptance
def test_server(app_docker_container: Container) -> None:
    http_driver = HTTPDriver()

    http_driver.healthcheck()
    upload_image_specification(http_driver)
    # ViewAllJobsSpecification()
    # CheckJobStatusSpecification()
    # DownloadThumbnailSpecification()
