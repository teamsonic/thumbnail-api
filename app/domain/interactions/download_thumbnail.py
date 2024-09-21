from typing import BinaryIO

from app.task_queue import get_broker


def download_thumbnail(job_id: str) -> BinaryIO:
    """Retrieve the thumbnail for the previously uploaded image

    :param job_id: The job's ID, as returned from the Broker
    :return: Binary image data wrapped in a file-like interface
    """
    return get_broker().get_result(job_id)
