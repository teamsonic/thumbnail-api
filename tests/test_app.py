"""Collection of acceptance tests."""

from typing import BinaryIO

import pytest
from docker.models.containers import Container

from app.exceptions import InvalidImage
from tests.conftest import square_image
from tests.exceptions import ImageTooLarge, MissingContentLength
from tests.specifications.adapters.http_driver import HTTPDriver
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
) -> None:
    """Test the application from the level of a consumer.

    These tests are performed against a running instance of the
    application and use an HTTP driver to assert the system
    specifications via an HTTP interface.

    :param app_docker_container: docker container running this application
    :return: None
    """
    http_driver = HTTPDriver()

    http_driver.healthcheck()
    upload_image_specification(http_driver)
    with pytest.raises(InvalidImage):
        upload_invalid_image_specification(http_driver)
    with pytest.raises(ImageTooLarge):
        http_driver.upload(size_too_large_image)
    with pytest.raises(MissingContentLength):
        http_driver.upload_no_content_length(square_image)
    # ViewAllJobsSpecification()
    # CheckJobStatusSpecification()
    # DownloadThumbnailSpecification()
