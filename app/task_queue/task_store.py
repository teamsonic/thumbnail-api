import io
import os
import shutil
import uuid
from enum import StrEnum
from pathlib import Path
from typing import BinaryIO, Iterable, Protocol

from PIL import Image

from app.exceptions import JobNotFound


class TaskStatus(StrEnum):
    PROCESSING = "Processing"
    SUCCEEDED = "Succeeded"
    ERROR = "Error"
    NOT_FOUND = "Not Found"


class TaskStoreBroker(Protocol):
    def add_task_to_queue(self, image: BinaryIO) -> str: ...

    def get_task_status(self, job_id: str) -> TaskStatus: ...

    def get_all_task_status(self) -> dict[TaskStatus, Iterable[str]]: ...

    def get_result(self, job_id: str) -> BinaryIO: ...

    def get_error(self, job_id: str) -> str: ...


class TaskStoreWorker(Protocol):
    def get_next_task(self) -> tuple[str, BinaryIO] | None: ...

    def register_task_complete(self, job_id: str, thumbnail: Image.Image) -> None: ...

    def register_task_error(self, job_id: str, error: Exception) -> None: ...


class FileSystemTaskStore(TaskStoreBroker, TaskStoreWorker):
    _in_folder = "in"
    _out_folder = "out"
    _error_folder = "error"

    def __init__(self, data_folder: str, thumbnail_format: str) -> None:
        self._root = Path(data_folder)
        self._thumbnail_format = thumbnail_format
        self._init_folders()

    def _init_folders(self) -> None:
        self._root.mkdir(exist_ok=True)
        self._folders: dict[str, Path] = {}

        for folder in [self._in_folder, self._out_folder, self._error_folder]:
            path = self._root.joinpath(folder)
            path.mkdir(exist_ok=True)
            self._folders[folder] = path

    def reset(self) -> None:
        shutil.rmtree(self._root, ignore_errors=True)
        self._init_folders()

    @property
    def in_folder(self) -> Path:
        return self._folders["in"]

    @property
    def out_folder(self) -> Path:
        return self._folders["out"]

    @property
    def error_folder(self) -> Path:
        return self._folders["error"]

    def _in_job_path(self, job_id: str) -> Path:
        return self.in_folder.joinpath(job_id)

    def _out_job_path(self, job_id: str) -> Path:
        return self.out_folder.joinpath(job_id)

    def _error_job_path(self, job_id: str) -> Path:
        return self.error_folder.joinpath(job_id)

    def _job_is_processing(self, job_id: str) -> bool:
        return self._in_job_path(job_id).exists()

    def _job_is_finished(self, job_id: str) -> bool:
        return self._out_job_path(job_id).exists()

    def _job_is_error(self, job_id: str) -> bool:
        return self._error_job_path(job_id).exists()

    def _job_ids_with_status(self, task_status: TaskStatus) -> Iterable[str]:
        folder: Path
        if task_status == TaskStatus.PROCESSING:
            folder = self.in_folder
        elif task_status == TaskStatus.SUCCEEDED:
            folder = self.out_folder
        elif task_status == TaskStatus.ERROR:
            folder = self.error_folder
        else:
            raise Exception(f"Unknown task status: {task_status}")
        return os.listdir(folder)

    def add_task_to_queue(self, image: BinaryIO) -> str:
        job_id = str(uuid.uuid4())
        self._in_job_path(job_id).write_bytes(image.read())
        return job_id

    def get_task_status(self, job_id: str) -> TaskStatus:
        if self._job_is_finished(job_id):
            return TaskStatus.SUCCEEDED
        elif self._job_is_processing(job_id):
            return TaskStatus.PROCESSING
        elif self._job_is_error(job_id):
            return TaskStatus.ERROR
        else:
            return TaskStatus.NOT_FOUND

    def get_all_task_status(self) -> dict[TaskStatus, Iterable[str]]:
        return {
            TaskStatus.PROCESSING: self._job_ids_with_status(TaskStatus.PROCESSING),
            TaskStatus.SUCCEEDED: self._job_ids_with_status(TaskStatus.SUCCEEDED),
            TaskStatus.ERROR: self._job_ids_with_status(TaskStatus.ERROR),
        }

    def get_result(self, job_id: str) -> BinaryIO:
        if self._job_is_finished(job_id):
            return io.BytesIO(self.out_folder.joinpath(job_id).read_bytes())
        raise JobNotFound(f"No completed job found with ID {job_id}")

    def get_error(self, job_id: str) -> str:
        if not self._job_is_error(job_id):
            raise JobNotFound(f"No error job found with ID {job_id}")
        return self._error_job_path(job_id).read_text("utf-8")

    def get_next_task(self) -> tuple[str, BinaryIO] | None:
        tasks = self._job_ids_with_status(TaskStatus.PROCESSING)
        try:
            job_id = next(iter(tasks))
        except StopIteration:
            return None

        image_path = self._in_job_path(job_id)
        image_data = io.BytesIO(image_path.read_bytes())
        os.remove(image_path)
        return job_id, image_data

    def register_task_complete(self, job_id: str, thumbnail: Image.Image) -> None:
        thumbnail_path = self._out_job_path(job_id)
        thumbnail.save(thumbnail_path, format=self._thumbnail_format)

    def register_task_error(self, job_id: str, error: Exception) -> None:
        error_path = self._error_job_path(job_id)
        error_path.write_text(str(error), "utf-8")
