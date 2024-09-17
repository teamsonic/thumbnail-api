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
from enum import StrEnum
from typing import BinaryIO, Generator

import docker
import pytest
from _pytest.fixtures import FixtureRequest
from docker.models.containers import Container

from app import settings

_ASSETS_PATH: str


def pytest_configure(config: pytest.Config) -> None:
    """Programmatically configure pytest environment just before testing begins.

    :param config: Global pytest configuration
    :return: None
    """
    global _ASSETS_PATH
    _ASSETS_PATH = f"{config.rootpath}/tests/assets"


class ImageType(StrEnum):
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


@pytest.fixture(scope="session")
def app_docker_container(request: FixtureRequest) -> Container:
    """Return a running docker container hosting this application

    This function will build a new image and start a new container,
    waiting until it is accepting requests before returning.

    Multiple test functions requesting this fixture will receive the same instance.

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

    container = client.containers.run(
        tag, ports={f"{settings.app_port}/tcp": settings.app_port}, detach=True
    )
    request.addfinalizer(container.remove)
    request.addfinalizer(container.stop)

    from tests.specifications.adapters.http_driver import HTTPDriver

    HTTPDriver.healthcheck()

    return container
