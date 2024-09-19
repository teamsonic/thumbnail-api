from typing import BinaryIO

from app.task_queue import broker


def download_thumbnail(job_id: str) -> BinaryIO:
    return broker.get_result(job_id)
