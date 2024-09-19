from typing import BinaryIO, Protocol

from PIL import Image

from app import settings


class ThumbnailDownloader(Protocol):
    def download(self, job_id: str) -> BinaryIO: ...


def download_thumbnail_specification(
    thumbnail_downloader: ThumbnailDownloader, job_id: str
) -> None:
    result = thumbnail_downloader.download(job_id)
    pil_image = Image.open(result)
    assert pil_image.size == settings.thumbnail_size
    assert pil_image.format == settings.thumbnail_file_type
