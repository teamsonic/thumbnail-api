from typing import BinaryIO

from fastapi import status
from fastapi.testclient import TestClient

from app.exceptions import InvalidImage, JobNotFound
from app.srv import app
from app.srv.models import AllJobs, JobStatusModel, UploadImageModel
from app.task_queue.task_store import TaskStatus
from tests.exceptions import ImageTooLarge, InvalidJobID, MissingContentLength
from tests.specifications.check_job_status import CheckJobStatus
from tests.specifications.get_all_job_ids import GetAllJobIds
from tests.specifications.upload_image import UploadImage


class HTTPTestDriver(UploadImage, GetAllJobIds, CheckJobStatus):
    def __init__(self) -> None:
        self.client = TestClient(app)

    def upload(self, file: BinaryIO) -> str:
        response = self.client.post("/upload_image", files={"file": file})
        status_code = response.status_code

        if status_code == status.HTTP_202_ACCEPTED:
            data = UploadImageModel.model_validate(response.json())
            return data.job_id
        elif status_code == status.HTTP_411_LENGTH_REQUIRED:
            raise MissingContentLength
        elif status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE:
            raise ImageTooLarge
        elif status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE:
            raise InvalidImage

        raise Exception(f"Unexpected status code: {status_code}")

    def check_job_status(self, job_id: str) -> tuple[TaskStatus, str | None]:
        response = self.client.get(f"/check_job_status/{job_id}")
        status_code = response.status_code

        if status_code == status.HTTP_200_OK:
            data = JobStatusModel.model_validate(response.json())
            return data.status, data.resource_url
        elif status_code == status.HTTP_400_BAD_REQUEST:
            raise InvalidJobID
        elif status_code == status.HTTP_404_NOT_FOUND:
            raise JobNotFound

        raise Exception(f"Unexpected status code: {status_code}")

    def get_all_job_ids(self) -> list[str]:
        response = self.client.get("/jobs")
        assert response.status_code == status.HTTP_200_OK
        data = AllJobs.model_validate(response.json())

        return data.job_ids
