from app import settings
from app.task_queue.broker import Broker
from app.task_queue.task_store import FileSystemTaskStore
from app.task_queue.worker import Worker

task_store = FileSystemTaskStore(
    settings.task_queue_data_folder, settings.thumbnail_file_type
)
broker = Broker(task_store)


def create_worker() -> Worker:
    return Worker(task_store)
