import uuid
from typing import BinaryIO, Iterable

from app.exceptions import JobNotFound
from app.task_queue.task_store import TaskStatus, TaskStoreBroker
from tests.conftest import ImageType, JobID


class StubbedTaskStoreBroker(TaskStoreBroker):
    def add_task_to_queue(self, image: BinaryIO) -> str:
        return str(uuid.uuid4())

    def get_task_status(self, job_id: str) -> TaskStatus:
        if job_id == JobID.COMPLETE:
            return TaskStatus.SUCCEEDED
        elif job_id == JobID.INCOMPLETE:
            return TaskStatus.PROCESSING
        elif job_id == JobID.ERROR:
            return TaskStatus.ERROR
        else:
            return TaskStatus.NOT_FOUND

    def get_all_task_status(self) -> dict[TaskStatus, Iterable[str]]:
        return {
            TaskStatus.PROCESSING: [JobID.INCOMPLETE],
            TaskStatus.SUCCEEDED: [JobID.COMPLETE],
            TaskStatus.ERROR: [JobID.ERROR],
        }

    def get_result(self, job_id: str) -> BinaryIO:
        if job_id == JobID.COMPLETE:
            return ImageType.THUMBNAIL.get_image()

        raise JobNotFound(f"Unexpected job_id: {job_id}")

    def get_error(self, job_id: str) -> str:
        if job_id == JobID.ERROR:
            return "this job failed because of reasons"

        raise Exception(f"Unexpected job_id: {job_id}")
