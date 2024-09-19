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
from fastapi import status
from pydantic import ValidationError
from requests import Response

from app import settings
from app.exceptions import InvalidImage, JobNotFound
from app.srv.models import JobStatusModel, UploadImageModel
from app.task_queue.task_store import TaskStatus
from tests.exceptions import ImageTooLarge, InvalidJobID, MissingContentLength
from tests.specifications.check_job_status import CheckJobStatus
from tests.specifications.upload_image import UploadImage


class HTTPDriver:
    """Base HTTPDriver class that all others inherit from

    Contains the fundamental logic to make HTTP requests to the server.
    """

    port = settings.app_port
    base_url = f"http://localhost:{port}"

    def _make_request(
        self, method: str, path: str, **kwargs: dict[str, Any]
    ) -> tuple[requests.Session, requests.PreparedRequest]:
        session = requests.session()
        request = requests.Request(method, f"{self.base_url}{path}", **kwargs)
        prepared = request.prepare()
        return session, prepared

    def _do_request(
        self, method: str, path: str, file: BinaryIO | None = None
    ) -> Response:
        kwargs = {}
        if file:
            kwargs["files"] = {"file": file}

        session, request = self._make_request(method, path, **kwargs)
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


class UploadImageHTTPDriver(HTTPDriver, UploadImage):
    """HTTPDriver subclass used to test-drive uploading images

    Methods:
    -------
    upload(self, file: BinaryIO) -> str: Main testing entrypoint that uploads a file
    upload_no_content_length(self, file: BinaryIO) -> str: A variant of the upload
    method that removes the "content-length" header to test edge cases.
    """

    @staticmethod
    def _verify_job_id_response(response: Response) -> str:
        """
        Validate the response, which should conform to the UploadImageModel schema

        :param response: Response object
        :return: The job_id as a string
        :raises: ValidationError if the data cannot be validated as an UploadImageModel
        """
        model = UploadImageModel(**response.json())
        return model.job_id

    def _validate_response(self, response: Response) -> str:
        try:
            job_id = self._verify_job_id_response(response)
            assert response.status_code == status.HTTP_202_ACCEPTED
            return job_id
        except ValidationError:
            status_code = response.status_code
            if status_code == status.HTTP_411_LENGTH_REQUIRED:
                raise MissingContentLength
            if status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE:
                raise ImageTooLarge
            if status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE:
                raise InvalidImage

        raise Exception("Could not validate response")

    def upload(self, file: BinaryIO) -> str:
        """Main upload_image testing entrypoint for the HTTPDriver

        Uploads a file and tries to parse the response to an UploadImageModel
        instance, which is the schema of a successful upload. If this validation
        fails, other assertions are made on the response data to raise the
        appropriate exceptions that error specifications are expecting.

        :param file: A file. It may or may not be an image.
        :return: A job_id as a string, as received from the server
        :raises: MissingContentLength if the response code is 411
        :raises: ImageTooLarge if the response code is 413
        :raises: InvalidImage if the response code is 415
        :raises: Exception if no expected responses were encountered
        """
        response = self._do_request("POST", "/upload_image", file)
        return self._validate_response(response)

    def upload_no_content_length(self, file: BinaryIO) -> str:
        """Does exactly what upload does, but removes the "content-length"
        header to test edge cases.

        :param file: A file. It may or may not be an image.
        :return: A job_id as a string, as received from the server
        """
        session, prepared = self._make_request(
            "POST", "/upload_image", files={"file": file}
        )
        del prepared.headers["content-length"]
        response = session.send(prepared)
        return self._validate_response(response)


class CheckJobStatusHTTPDriver(HTTPDriver, CheckJobStatus):
    """HTTPDriver subclass for test-driving the checking of job statuses

    Methods:
    --------
    check_job_status(self, job_id: str) -> Tuple[bool, str | None]:
        Main entrypoint for job status checking testing. A request is made
        to the server with the provided job_id and the response is examined.
    """

    def check_job_status(self, job_id: str) -> tuple[TaskStatus, str | None]:
        """Main check_job_status testing entrypoint for the HTTPDriver

        Makes a request for job status using a provided job_id.

        :param job_id: The id of the job
        :return: tuple of the job status and a resource_url if finished
        """
        response = self._do_request("GET", f"/check_job_status/{job_id}")
        return self._validate_response(response)

    @staticmethod
    def _validate_response(response: Response) -> tuple[TaskStatus, str | None]:
        try:
            model = JobStatusModel(**response.json())
            assert response.status_code == status.HTTP_200_OK
            return model.status, model.resource_url
        except ValidationError:
            if response.status_code == status.HTTP_400_BAD_REQUEST:
                raise InvalidJobID
            if response.status_code == status.HTTP_404_NOT_FOUND:
                raise JobNotFound

        raise Exception(f"Could not validate response: {response.json()}")
