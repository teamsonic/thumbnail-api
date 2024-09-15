from tests.specifications.adapters.adapters import UploadImageAdapter
from tests.specifications.upload_image import upload_image_specification


def test_upload_image() -> None:
    """
    Execute the upload image interaction
    to assert that the behavior matches the specification
    """
    upload_image_specification(UploadImageAdapter())
