import uuid
from typing import BinaryIO

from PIL import Image, UnidentifiedImageError

from app.exceptions import InvalidImage


def upload_image(image: BinaryIO) -> uuid.UUID:
    """Accept image data and launch a task to create a thumbnail of it.

    The task is performed asynchronously and has an associated id when created.
    This id is returned and can be used to query the status of the job.

    :param image: BinaryIO file of an image to be resized
    :return: UUID uniquely identifying the task
    :raises: InvalidImage if the file is not an image
    """
    try:
        Image.open(image).verify()
    except UnidentifiedImageError as e:
        raise InvalidImage(e)
    return uuid.uuid4()
