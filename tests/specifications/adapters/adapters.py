from typing import BinaryIO

from app.domain.interactions.check_job_status import check_job_status
from app.domain.interactions.download_thumbnail import download_thumbnail
from app.domain.interactions.get_all_job_ids import get_all_job_ids
from app.domain.interactions.upload_image import upload_image
from app.task_queue.task_store import TaskStatus
from tests.specifications.check_job_status import CheckJobStatus
from tests.specifications.download_thumbnail import ThumbnailDownloader
from tests.specifications.get_all_job_ids import GetAllJobIds
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


class GetAllJobIdsAdapter(GetAllJobIds):
    def get_all_job_ids(self) -> list[str]:
        return get_all_job_ids()


class ThumbnailDownloaderAdapter(ThumbnailDownloader):
    def download(self, job_id: str) -> BinaryIO:
        return download_thumbnail(job_id)
