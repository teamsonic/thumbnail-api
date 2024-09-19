"""Module containing global pytest fixtures

See https://docs.pytest.org/en/stable/reference/fixtures.html

Fixtures:

app_docker_container: Docker Container running the thumbnail-api
wide_image: File object of a wide image, which is wider than it is tall.
tall_image: File object of a tall image, which is taller than it is wide.

Other Exports:

get_wide_image: Function retuning the resolved value of the wide_image fixture
for functions not able to use the fixture version.
"""

import io
import subprocess
import threading
from enum import StrEnum
from typing import BinaryIO, Generator

import docker
import pytest
from _pytest.fixtures import FixtureRequest
from docker.models.containers import Container

from app import settings
from app.task_queue import broker, task_store
from app.task_queue.broker import Broker
from tests.task_queue.stubbed_task_store import StubbedTaskStoreBroker as TSB

_ASSETS_PATH: str
ACCEPTANCE_TEST_LOGS: str = "acceptance_test_server_logs"


def pytest_configure(config: pytest.Config) -> None:
    """Programmatically configure pytest environment just before testing begins.

    :param config: Global pytest configuration
    :return: None
    """
    global _ASSETS_PATH
    _ASSETS_PATH = f"{config.rootpath}/tests/assets"

    pytest.register_assert_rewrite("tests.specifications")


class ImageType(StrEnum):
    """
    Used to test uploading and creating thumbnails of various types of files
    """

    SQUARE = "日本電波塔.jpg"
    WIDE = "日本電波塔より横.jpg"
    TALL = "日本電波塔より縦.jpg"
    SIZE_TOO_LARGE = "too_large.jpg"
    NOT_AN_IMAGE = "not_an_image.txt"

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
    return TSB.JobID.COMPLETE


@pytest.fixture
def job_id_incomplete() -> str:
    """Provides a job id that corresponds to a job whose status is incomplete."""
    return TSB.JobID.INCOMPLETE


@pytest.fixture
def job_id_error() -> str:
    """Provides a job id that corresponds to a job whose status is error."""
    return TSB.JobID.ERROR


@pytest.fixture
def job_id_not_found() -> str:
    """Provides a job id that does not correspond to a job."""
    return TSB.JobID.NOT_FOUND


@pytest.fixture
def job_id_invalid() -> str:
    """Provides an invalid job id. i.e. cannot be parsed as a UUID."""
    return TSB.JobID.INVALID


@pytest.fixture(scope="function")
def task_broker() -> Generator[Broker, None, None]:
    """Get the default task_queue broker.

    This fixture just returns the Broker singleton,
    but more importantly cleans up the leftover files afterward.
    """
    task_store.reset()
    yield broker
    task_store.reset()


@pytest.fixture(scope="session")
def stubbed_broker() -> Broker:
    """Use a Broker interacting with a stubbed, stateless TaskStore"""
    return Broker(TSB())


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
        f"docker build --tag {tag} .", shell=True, stderr=subprocess.STDOUT, timeout=60
    )
    request.addfinalizer(lambda: client.images.get(tag).remove())

    volume_name = f"{settings.app_name}-acceptance-test"
    volume = client.volumes.get(volume_name)
    volume.remove(force=True)
    container = client.containers.run(
        tag,
        ports={f"{settings.app_port}/tcp": settings.app_port},
        detach=True,
        volumes=[f"{volume_name}:/app"],
    )

    request.addfinalizer(container.remove)
    request.addfinalizer(container.stop)

    from tests.specifications.adapters.http_driver import HTTPDriver

    HTTPDriver.healthcheck()

    def docker_logging_thread() -> None:
        with open(ACCEPTANCE_TEST_LOGS, "wb") as f:
            for line in container.logs(stream=True):
                message = b"\n" + line.strip()
                f.write(message)

    thread = threading.Thread(target=docker_logging_thread)
    thread.start()

    return container
