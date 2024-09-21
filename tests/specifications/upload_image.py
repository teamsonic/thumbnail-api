"""
Specification(s) related to the interaction of providing
image data and receiving a job id in return.
"""

import uuid
from typing import BinaryIO, Protocol

from tests.conftest import ImageType


class UploadImage(Protocol):
    """
    A protocol describing the interface for uploading an image.

    "Send image binary data, get a job id in return"
    """

    def upload(self, file: BinaryIO) -> str: ...


def upload_image_specification(image_uploader: UploadImage) -> str:
    """Describes the specification for uploading an image to become a thumbnail

    "When an image is uploaded, an uuid-compliant job_id is returned"

    :param image_uploader: Any object implementing the UploadImage protocol
    :return: The job id generated
    :raises: Exception if a UUID was not returned
    """
    response = image_uploader.upload(ImageType.SQUARE.get_image())
    try:
        uuid.UUID(response)
    except ValueError:
        raise Exception(f"Expected return to be UUID compliant, but got {response}")

    return response


def upload_invalid_image_specification(image_uploader: UploadImage) -> None:
    """Describes the specification for uploading a file that is not an image

    "When an invalid file type is uploaded, an error should be returned"

    How the error is formed depends on the driver of the specification.
    The job of this specification is simply to trigger the error and allow
    the drivers to perform further assertions downstream.

    :param image_uploader: Any object implementing the UploadImage protocol
    """
    image_uploader.upload(ImageType.NOT_AN_IMAGE.get_image())
