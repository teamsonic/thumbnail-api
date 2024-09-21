"""Specifications for what should happen when a thumbnail is downloaded"""

from typing import BinaryIO, Protocol

from PIL import Image

from app import settings


class ThumbnailDownloader(Protocol):
    """
    A protocol describing the interface for downloading a thumbnail.

    "Send a job_id, get the thumbnail image binary data"
    """

    def download(self, job_id: str) -> BinaryIO: ...


def download_thumbnail_specification(
    thumbnail_downloader: ThumbnailDownloader, job_id: str
) -> None:
    """Describes the specification of requesting the thumbnail.

    "When the result of the completed image processing is requested,
    a thumbnail that meets the required size and format requirements
    is returned."

    :param thumbnail_downloader: Object implementing the ThumbnailDownloader protocol
    :param job_id: The job id to check
    """
    result = thumbnail_downloader.download(job_id)
    pil_image = Image.open(result)
    assert pil_image.size == settings.thumbnail_size
    assert pil_image.format == settings.thumbnail_file_type
