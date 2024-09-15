"""
Specification(s) related to the interaction of providing
image data and receiving a job id in return.
"""
import uuid
from typing import BinaryIO, Protocol


class UploadImage(Protocol):
    """
    A protocol describing the interface for uploading an image.

    Methods
    -------
    upload(file: BinaryIO) -> str
        Accepts a file for thumbnail processing and returns the job id
        as a string compliant with UUID specification.
    """

    def upload(self, file: BinaryIO) -> str: ...


def upload_image_specification(image_uploader: UploadImage) -> None:
    with open("assets/日本電波塔.jpg", "rb") as f:
        response = image_uploader.upload(f)
        try:
            uuid.UUID(response)
        except ValueError:
            raise Exception(f"Expected return to be UUID compliant, but got {response}")
