import pytest

from app.exceptions import InvalidImage
from tests.specifications.adapters.adapters import UploadImageAdapter
from tests.specifications.upload_image import (
    upload_image_specification,
    upload_invalid_image_specification,
)


def test_upload_image() -> None:
    """
    Execute the upload image interaction
    to assert that the behavior matches the specification
    """
    upload_image_specification(UploadImageAdapter())


def test_upload_invalid_image() -> None:
    """
    Execute the upload invalid image interaction
    and verify a InvalidImage is raised
    """
    with pytest.raises(InvalidImage):
        upload_invalid_image_specification(UploadImageAdapter())
