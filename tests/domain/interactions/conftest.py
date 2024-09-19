import app.task_queue
from app.task_queue.broker import Broker
from tests.task_queue.stubbed_task_store import StubbedTaskStoreBroker


def pytest_configure() -> None:
    app.task_queue.broker = Broker(StubbedTaskStoreBroker())
