"""Module containing logic to drive testing via HTTP.

HTTPDriver subclasses in this module use a combination of HTTP
and specification protocols to assert that the specifications
hold via an HTTP interface.

Exports:

HTTPDriver - Base class for HTTP test-driving
UploadImageHTTPDriver - HTTP driver to assert behavior around uploading images
CheckJobStatusHTTPDriver - HTTP driver to assert behavior around checking the
job status of image -> thumbnail conversion
"""

from time import sleep
from typing import Any, BinaryIO

import requests
from requests import Response

from app import settings


class HTTPClientDriver:
    """Base HTTPDriver class that all others inherit from

    Contains the fundamental logic to make HTTP requests to the server.
    """

    port = settings.app_port
    base_url = f"http://localhost:{port}"

    def make_request(
        self, method: str, path: str, **kwargs: dict[str, Any]
    ) -> tuple[requests.Session, requests.PreparedRequest]:
        session = requests.session()
        request = requests.Request(method, f"{self.base_url}{path}", **kwargs)
        prepared = request.prepare()
        return session, prepared

    def do_request(
        self, method: str, path: str, file: BinaryIO | None = None
    ) -> Response:
        kwargs = {}
        if file:
            kwargs["files"] = {"file": file}

        session, request = self.make_request(method, path, **kwargs)
        return session.send(request)

    @classmethod
    def healthcheck(cls, timeout: int = 30) -> bool:
        """Attempt to get a heartbeat from the server

        :param timeout: Number of seconds to wait for heartbeat
        :return: True if the server is healthy, False otherwise
        :raises: Exception if the heartbeat fails within the timeout
        """
        elapsed = 0
        err: Exception | None = None

        while elapsed < timeout:
            try:
                response = requests.get(cls.base_url + "/healthcheck")
            except requests.exceptions.RequestException as e:
                err = e
            else:
                return dict(response.json()).get("status") == "healthy"
            sleep(1)
            elapsed += 1

        raise Exception("Server could not be reached") from err
