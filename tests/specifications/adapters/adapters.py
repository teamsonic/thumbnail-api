from typing import BinaryIO

from app.domain.interactions.upload_image import upload_image
from tests.specifications.upload_image import UploadImage


class UploadImageAdapter(UploadImage):
    """
    Adapts the specification to the shape of the interaction
    """

    def upload(self, file: BinaryIO) -> str:
        uuid = upload_image(file)
        return str(uuid)

