from tests.specifications.adapters.adapters import UploadImageAdapter
from tests.specifications.upload_image import upload_image_specification


def test_upload_image() -> None:
    """
    Fundamental interaction test to demonstrate that the interaction to
    upload an image conforms to the specification
    """
    upload_image_specification(UploadImageAdapter())
