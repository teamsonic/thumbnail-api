import io
from typing import BinaryIO

from fastapi import status
from fastapi.testclient import TestClient

from app.exceptions import InvalidImage, JobNotFound
from app.srv import AllJobsModel, JobStatusModel, Routes, UploadImageModel, app
from app.task_queue import TaskStatus
from tests.exceptions import ImageTooLarge, MissingContentLength
from tests.specifications.check_job_status import CheckJobStatus
from tests.specifications.download_thumbnail import ThumbnailDownloader
from tests.specifications.get_all_job_ids import GetAllJobIds
from tests.specifications.upload_image import UploadImage


class HTTPTestDriver(UploadImage, GetAllJobIds, CheckJobStatus, ThumbnailDownloader):
    """
    Simulate HTTP requests with a FastAPI test client. Great for asserting the
    behavior of the application's HTTP interface without needing a running server.

    Specifications will utilize this class to drive application
    behavior assertions when done via HTTP.
    """

    def __init__(self) -> None:
        self.client = TestClient(app)

    def upload(self, file: BinaryIO) -> str:
        response = self.client.post(Routes.UPLOAD_IMAGE, files={"file": file})
        status_code = response.status_code

        if status_code == status.HTTP_202_ACCEPTED:
            data = UploadImageModel.model_validate(response.json())
            assert response.headers["Location"] == Routes.CHECK_JOB_STATUS.format(
                job_id=data.job_id
            )
            return data.job_id
        elif status_code == status.HTTP_411_LENGTH_REQUIRED:
            raise MissingContentLength
        elif status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE:
            raise ImageTooLarge
        elif status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE:
            raise InvalidImage

        raise Exception(f"Unexpected status code: {status_code}")

    def check_job_status(self, job_id: str) -> tuple[TaskStatus, str | None]:
        response = self.client.get(
            Routes.CHECK_JOB_STATUS.format(job_id=job_id), follow_redirects=False
        )
        status_code = response.status_code

        if status_code in (status.HTTP_200_OK, status.HTTP_303_SEE_OTHER):
            data = JobStatusModel.model_validate(response.json())
            if status_code == status.HTTP_303_SEE_OTHER:
                assert response.headers["Location"] == Routes.DOWNLOAD_THUMBNAIL.format(
                    job_id=job_id
                )
            return data.status, data.resource_url
        elif status_code == status.HTTP_404_NOT_FOUND:
            raise JobNotFound

        raise Exception(f"Unexpected status code: {status_code}")

    def get_all_job_ids(self) -> list[str]:
        response = self.client.get(Routes.JOBS)
        assert response.status_code == status.HTTP_200_OK
        data = AllJobsModel.model_validate(response.json())

        return data.job_ids

    def download(self, job_id: str) -> BinaryIO:
        response = self.client.get(Routes.DOWNLOAD_THUMBNAIL.format(job_id=job_id))
        status_code = response.status_code

        if status_code == status.HTTP_200_OK:
            return io.BytesIO(response.content)
        elif status_code == status.HTTP_404_NOT_FOUND:
            raise JobNotFound

        raise Exception(f"Unexpected status code: {status_code}")
