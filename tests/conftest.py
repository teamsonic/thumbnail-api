"""Module containing global pytest fixtures and configuration

See https://docs.pytest.org/en/stable/reference/fixtures.html
"""

import io
import subprocess
import threading
from enum import StrEnum
from pathlib import Path
from typing import BinaryIO

import docker
import pytest
from _pytest.fixtures import FixtureRequest
from docker.errors import NotFound
from docker.models.containers import Container

from app import settings
from tests.specifications.adapters.http_client_driver import HTTPClientDriver

_ASSETS_PATH: str
ACCEPTANCE_TEST_ARTIFACTS_PATH: str


def pytest_configure(config: pytest.Config) -> None:
    """Programmatically configure pytest environment just before testing begins.

    :param config: Global pytest configuration
    """
    global _ASSETS_PATH
    global ACCEPTANCE_TEST_ARTIFACTS_PATH
    _ASSETS_PATH = f"{config.rootpath}/tests/assets"
    ACCEPTANCE_TEST_ARTIFACTS_PATH = (
        f"{config.rootpath}/tests/acceptance_test_artifacts"
    )
    Path(ACCEPTANCE_TEST_ARTIFACTS_PATH).mkdir(exist_ok=True)


class JobID(StrEnum):
    """Used to test retrieving job id statuses"""

    COMPLETE = "0c895999-7a69-4770-b116-7eff01a57b99"
    INCOMPLETE = "1d295999-7a69-4770-b116-7eff01a57b99"
    ERROR = "3af56290-f0da-420e-b9bb-c748f4a08ca6"
    NOT_FOUND = "2e395999-7a69-4770-b116-7eff01a57b99"
    INVALID = "2-7a69-4770-b116-7eff01a57b99"


class ImageType(StrEnum):
    """
    Used to test uploading and creating thumbnails of various types of files
    """

    SQUARE = "日本電波塔.jpg"
    WIDE = "日本電波塔より横.jpg"
    TALL = "日本電波塔より縦.jpg"
    WEBP = "日本電波塔.webp"
    PNG = "日本電波塔.png"
    SIZE_TOO_LARGE = "too_large.jpg"
    NOT_AN_IMAGE = "not_an_image.txt"
    THUMBNAIL = JobID.COMPLETE

    def get_image(self) -> BinaryIO:
        with open(f"{_ASSETS_PATH}/{self}", "rb") as f:
            return io.BytesIO(f.read())


@pytest.fixture(scope="function")
def square_image() -> BinaryIO:
    """A square image.

    :return: A file object that is safe to mutate.
    """
    return ImageType.SQUARE.get_image()


@pytest.fixture(scope="function")
def wide_image(request: FixtureRequest) -> BinaryIO:
    """A wide image, which is wider than it is tall.

    :return: A file object that is safe to mutate.
    """
    return ImageType.WIDE.get_image()


@pytest.fixture(scope="function")
def tall_image() -> BinaryIO:
    """A tall image, which is taller than it is wide.

    :return: A file object that is safe to mutate.
    """
    return ImageType.TALL.get_image()


@pytest.fixture(scope="function")
def webp_image() -> BinaryIO:
    """An image in webp format

    :return: A file object that is safe to mutate.
    """
    return ImageType.WEBP.get_image()


@pytest.fixture(scope="function")
def png_image() -> BinaryIO:
    """An image in png format

    :return: A file object that is safe to mutate.
    """
    return ImageType.PNG.get_image()


@pytest.fixture(scope="function")
def size_too_large_image() -> BinaryIO:
    """An image with a content length greater than what the web server allows .

    :return: A file object that is safe to mutate.
    """
    return ImageType.SIZE_TOO_LARGE.get_image()


@pytest.fixture(scope="function")
def not_an_image() -> BinaryIO:
    """Not an image. Used for testing error conditions where an image is expected.

    :return: A file object that is safe to mutate.
    """
    return ImageType.NOT_AN_IMAGE.get_image()


@pytest.fixture
def job_id_complete() -> str:
    """Provides a job id that corresponds to a job whose status is complete."""
    return JobID.COMPLETE


@pytest.fixture
def job_id_incomplete() -> str:
    """Provides a job id that corresponds to a job whose status is incomplete."""
    return JobID.INCOMPLETE


@pytest.fixture
def job_id_error() -> str:
    """Provides a job id that corresponds to a job whose status is error."""
    return JobID.ERROR


@pytest.fixture
def job_id_not_found() -> str:
    """Provides a job id that does not correspond to a job."""
    return JobID.NOT_FOUND


@pytest.fixture
def job_id_invalid() -> str:
    """Provides an invalid job id. i.e. cannot be parsed as a UUID."""
    return JobID.INVALID


@pytest.fixture(scope="session")
def app_docker_container(request: FixtureRequest) -> Container:
    """Return a running docker container hosting this application

    This function will build a new image and start a new container,
    waiting until it is accepting requests before returning.

    Multiple test functions requesting this fixture will receive the same instance.
    Logs are piped and written out to a file which can be examined after testing.

    :param request: A pytest.FixtureRequest instance used for cleanup
    :return: A running Container
    :raises: TimeoutError if the container did not respond to
    health checks before the timeout.
    :raises: Exception if any other exception occurs.
    """
    client = docker.from_env()
    tag = f"{settings.app_name}:acceptance-test"

    # TODO: The subprocess call intentionally subverts the SDK as it still has
    # no support for BuildKit, which is required by the caching done in the Dockerfile.
    # Hopefully support will be added soon.
    # See https://github.com/docker/docker-py/issues/2230
    subprocess.check_output(
        f"docker build --tag {tag} .", shell=True, stderr=subprocess.STDOUT
    )
    request.addfinalizer(lambda: client.images.get(tag).remove(force=True))

    volume_name = f"{settings.app_name}-acceptance-test"
    try:
        volume = client.volumes.get(volume_name)
    except NotFound:
        pass
    else:
        volume.remove(force=True)

    container = client.containers.run(
        tag,
        ports={f"{settings.app_port}/tcp": settings.app_port},
        detach=True,
        volumes=[f"{volume_name}:/app"],
    )

    request.addfinalizer(container.remove)
    request.addfinalizer(container.stop)

    HTTPClientDriver.healthcheck()

    def docker_logging_thread() -> None:
        with open(f"{ACCEPTANCE_TEST_ARTIFACTS_PATH}/logs", "wb") as f:
            for line in container.logs(stream=True):
                message = b"\n" + line.strip()
                f.write(message)

    thread = threading.Thread(target=docker_logging_thread)
    thread.start()

    return container
