import app.task_queue
from app.task_queue import Broker
from tests.task_queue.stubbed_task_store import StubbedTaskStoreBroker


def pytest_configure() -> None:
    """Package level pytest configuration

    This just patches the get_broker function to return
    a stubbed version of a task store for unit testing.
    """
    app.task_queue.get_broker = lambda: Broker(StubbedTaskStoreBroker())
