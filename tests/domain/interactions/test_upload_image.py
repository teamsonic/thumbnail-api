"""Assert behavior for uploading an image"""

from typing import BinaryIO

import pytest

from app.exceptions import InvalidImage
from tests.exceptions import ImageTooLarge
from tests.specifications.adapters.adapters import UploadImageAdapter
from tests.specifications.adapters.http_test_driver import HTTPTestDriver
from tests.specifications.upload_image import (
    upload_image_specification,
    upload_invalid_image_specification,
)


class TestUploadImage:
    """
    Drive the specification for "uploading" a file directly
    without any interface. Unit tests.
    """

    def test_upload_image(self) -> None:
        upload_image_specification(UploadImageAdapter())

    def test_upload_invalid_image(self) -> None:
        with pytest.raises(InvalidImage):
            upload_invalid_image_specification(UploadImageAdapter())


class TestUploadImageHTTP:
    """
    Drive the specification for uploading a file
    via an HTTP interface.
    """

    def test_upload_image_http(self) -> None:
        upload_image_specification(HTTPTestDriver())

    def test_upload_invalid_image_http(self) -> None:
        with pytest.raises(InvalidImage):
            upload_invalid_image_specification(HTTPTestDriver())

    def test_upload_too_large_image_http(self, size_too_large_image: BinaryIO) -> None:
        with pytest.raises(ImageTooLarge):
            HTTPTestDriver().upload(size_too_large_image)
