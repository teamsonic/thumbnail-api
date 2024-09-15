from time import sleep
from typing import BinaryIO

import requests

from app import settings
from app.models import UploadImageModel
from tests.specifications.upload_image import UploadImage


class HTTPDriver(UploadImage):
    """
    Drives the image uploading specification conformity via HTTP
    """

    port = settings.app_port
    base_url = f"http://localhost:{port}"

    def upload(self, file: BinaryIO) -> str:
        response = requests.post(self.base_url + "/upload_image", files={"file": file})
        data = UploadImageModel(**response.json())
        return data.serialize_job_id(data.job_id)

    @classmethod
    def healthcheck(cls, timeout: int = 30) -> bool:
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
