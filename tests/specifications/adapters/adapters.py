from typing import BinaryIO

from app.domain.interactions.check_job_status import check_job_status
from app.domain.interactions.upload_image import upload_image
from app.task_queue.task_store import TaskStatus
from tests.specifications.check_job_status import CheckJobStatus
from tests.specifications.upload_image import UploadImage


class UploadImageAdapter(UploadImage):
    """
    Adapts the upload_image specification
    to the shape of the upload_image interaction
    """

    def upload(self, file: BinaryIO) -> str:
        response = upload_image(file)
        return str(response)


class CheckJobStatusAdapter(CheckJobStatus):
    """
    Adapts the check_job_status specification
    to the shape of the check_job_status interaction
    """

    def check_job_status(self, job_id: str) -> tuple[TaskStatus, str | None]:
        return check_job_status(job_id)
