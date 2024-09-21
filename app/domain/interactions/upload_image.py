from typing import BinaryIO

from PIL import Image, UnidentifiedImageError

from app.exceptions import InvalidImage
from app.task_queue import get_broker


def upload_image(image: BinaryIO) -> str:
    """Accept image data and launch a task to create a thumbnail of it.

    The task is performed asynchronously and has an associated id when created.
    This id is returned and can be used to query the status of the job.

    :param image: BinaryIO file of an image to be resized
    :return: uuid-compliant str uniquely identifying the task
    :raises: InvalidImage if the file type is not an image or not
        an image type supported by the image processing library.
    """
    try:
        Image.open(image).verify()
    except UnidentifiedImageError as e:
        raise InvalidImage(e)

    image.seek(0)
    return get_broker().add_task(image)
