"""Module containing global pytest fixtures

See https://docs.pytest.org/en/stable/reference/fixtures.html
"""

import docker
import pytest
from _pytest.fixtures import FixtureRequest
from docker.models.containers import Container

from app import settings
from tests.specifications.adapters.http_driver import HTTPDriver


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
    image = client.images.build(path=".", tag=tag)[0]
    request.addfinalizer(lambda: image.remove(force=True))

    container = client.containers.run(
        tag, ports={f"{settings.app_port}/tcp": settings.app_port}, detach=True
    )
    request.addfinalizer(container.remove)
    request.addfinalizer(container.stop)

    try:
        HTTPDriver.healthcheck()
    except Exception as e:
        raise TimeoutError from e

    return container
