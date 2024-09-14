import docker
import pytest
from _pytest.fixtures import FixtureRequest
from docker.models.containers import Container

from app import settings
from app.specifications.adapters.http_driver import HTTPDriver


@pytest.fixture(scope="session")
def app_docker_container(request: FixtureRequest) -> Container:
    client = docker.from_env()

    tag = f"{settings.app_name}:acceptance-test"
    image = client.images.build(path=".", tag=tag)[0]
    request.addfinalizer(lambda: image.remove(force=True))

    container = client.containers.run(
        tag, ports={f"{settings.app_port}/tcp": settings.app_port}, detach=True
    )
    request.addfinalizer(container.remove)
    request.addfinalizer(container.stop)

    HTTPDriver.healthcheck()
    return container
