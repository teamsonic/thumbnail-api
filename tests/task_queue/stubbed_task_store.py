import io
import uuid
from enum import StrEnum
from typing import BinaryIO, Iterable

from app.task_queue.task_store import TaskStatus, TaskStoreBroker


class StubbedTaskStoreBroker(TaskStoreBroker):
    class JobID(StrEnum):
        """Used to test retrieving job id statuses"""

        COMPLETE = "0c895999-7a69-4770-b116-7eff01a57b99"
        INCOMPLETE = "1d295999-7a69-4770-b116-7eff01a57b99"
        ERROR = "5t895999-7a69-4770-b116-7eff01a57b99"
        NOT_FOUND = "2e395999-7a69-4770-b116-7eff01a57b99"
        INVALID = "2-7a69-4770-b116-7eff01a57b99"

    def add_task_to_queue(self, image: BinaryIO) -> str:
        return str(uuid.uuid4())

    def get_task_status(self, job_id: str) -> TaskStatus:
        if job_id == self.JobID.COMPLETE:
            return TaskStatus.SUCCEEDED
        elif job_id == self.JobID.INCOMPLETE:
            return TaskStatus.PROCESSING
        elif job_id == self.JobID.ERROR:
            return TaskStatus.ERROR
        else:
            return TaskStatus.NOT_FOUND

    def get_all_task_status(self) -> dict[TaskStatus, Iterable[str]]:
        return {
            TaskStatus.PROCESSING: [self.JobID.INCOMPLETE],
            TaskStatus.SUCCEEDED: [self.JobID.COMPLETE],
            TaskStatus.ERROR: [self.JobID.ERROR],
        }

    def get_result(self, job_id: str) -> BinaryIO:
        if job_id == self.JobID.COMPLETE:
            return io.BytesIO()

        raise Exception(f"Unexpected job_id: {job_id}")

    def get_error(self, job_id: str) -> str:
        if job_id == self.JobID.ERROR:
            return "this job failed because of reasons"

        raise Exception(f"Unexpected job_id: {job_id}")
