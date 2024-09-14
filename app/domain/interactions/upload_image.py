from typing import BinaryIO


def upload_image(image: BinaryIO) -> dict[str, str]:
    """
    Given an image, create an asynchronous task to resize the image to a thumbnail
    and return the id of the job. This id can be used to query the status of the job

    :param image: File expected to represent data of an image to be resized
    :return: A dict containing the id of the job
    """
    return {"id": "1234"}
