import uuid
from typing import BinaryIO

import pytest
from _pytest.fixtures import FixtureRequest

from app.exceptions import JobNotFound
from app.task_queue import task_store
from app.task_queue.broker import Broker
from app.task_queue.task_store import TaskStatus
from app.task_queue.worker import Worker


def test_broker_worker_interactions(
    square_image: BinaryIO,
    not_an_image: BinaryIO,
    request: FixtureRequest,
) -> None:
    """
    Test all interactions with the broker, synchronously simulating
    the behavior of the worker where necessary
    """
    request.addfinalizer(lambda: task_store.reset())
    broker = Broker(task_store)
    worker = Worker(task_store)

    # assert the worker has no tasks
    assert not worker._get_task()

    job_id = broker.add_task(square_image)
    uuid.UUID(job_id)  # Assert job_id conforms to the UUID spec

    assert broker.task_status(job_id) == TaskStatus.PROCESSING
    with pytest.raises(JobNotFound):
        broker.get_result(job_id)  # Job has not completed yet

    task = worker._get_task()
    assert task is not None

    worker._do_task(*task)
    assert broker.task_status(job_id) == TaskStatus.SUCCEEDED

    broker.get_result(job_id)  # No exception as task is succeeded now

    # Expect an error when a non-image is provided
    not_an_image_job_id = broker.add_task(not_an_image)
    task = worker._get_task()
    assert task is not None
    worker._do_task(*task)
    assert broker.task_status(not_an_image_job_id) == TaskStatus.ERROR
    # Because this job failed, this call should return a message
    assert broker.get_error_result(not_an_image_job_id)

    # Assert getting all results
    processing_job_id = broker.add_task(square_image)
    results = broker.get_all_results()
    assert job_id in results[TaskStatus.SUCCEEDED]
    assert not_an_image_job_id in results[TaskStatus.ERROR]
    assert processing_job_id in results[TaskStatus.PROCESSING]

    # Assert an error when providing an ID that does not correspond to a job
    with pytest.raises(JobNotFound):
        broker.get_result(str(uuid.uuid4()))
