from time import sleep
from typing import Any, BinaryIO, Tuple

import requests
from fastapi import status
from pydantic import ValidationError

from app import settings
from app.exceptions import InvalidImage
from app.models import UploadImageModel
from tests.exceptions import ImageTooLarge, MissingContentLength
from tests.specifications.upload_image import UploadImage


class HTTPDriver(UploadImage):
    """
    Drives the image uploading specification conformity via HTTP
    """

    port = settings.app_port
    base_url = f"http://localhost:{port}"

    def _make_request(
        self, path: str, file: BinaryIO
    ) -> Tuple[requests.Session, requests.PreparedRequest]:
        session = requests.session()
        request = requests.Request(
            "POST", f"{self.base_url}{path}", files={"file": file}
        )
        prepared = request.prepare()
        return session, prepared

    def _do_request(self, path: str, file: BinaryIO) -> dict[str, Any]:
        session, request = self._make_request(path, file)
        response = session.send(request)
        return dict(response.json())

    @staticmethod
    def _verify_job_id_response(data: dict[str, Any]) -> str:
        """
        Validate the response, which should conform to the UploadImageModel schema

        :param data: Dict form of JSON data returned directly from upload request
        :return: The job_id as a string
        :raises: ValidationError if the data cannot be validated as an UploadImageModel
        """
        model = UploadImageModel(**data)
        return model.serialize_job_id(model.job_id)

    def _validate_response(self, data: dict[str, Any]) -> str:
        try:
            return self._verify_job_id_response(data)
        except ValidationError:
            status_code = data["status_code"]
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
        data = self._do_request("/upload_image", file)
        return self._validate_response(data)

    def upload_no_content_length(self, file: BinaryIO) -> str:
        session, prepared = self._make_request("/upload_image", file)
        del prepared.headers["content-length"]
        response = session.send(prepared)
        return self._validate_response(dict(response.json()))

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
                response = requests.post(cls.base_url + "/healthcheck")
            except requests.exceptions.RequestException as e:
                err = e
            else:
                return dict(response.json()).get("status") == "healthy"
            sleep(1)
            elapsed += 1

        raise Exception("Server could not be reached") from err
