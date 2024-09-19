import pytest

from app.exceptions import JobNotFound
from tests.specifications.adapters.adapters import ThumbnailDownloaderAdapter
from tests.specifications.adapters.http_test_driver import HTTPTestDriver
from tests.specifications.download_thumbnail import download_thumbnail_specification


def test_download_thumbnail(job_id_complete: str) -> None:
    download_thumbnail_specification(ThumbnailDownloaderAdapter(), job_id_complete)


class TestDownloadThumbnailHTTP:
    def test_download_thumbnail(self, job_id_complete: str) -> None:
        download_thumbnail_specification(HTTPTestDriver(), job_id_complete)

    def test_download_thumbnail_not_found(self, job_id_incomplete: str) -> None:
        with pytest.raises(JobNotFound):
            download_thumbnail_specification(HTTPTestDriver(), job_id_incomplete)
