import uuid
from typing import BinaryIO

import pytest

from app.exceptions import JobNotFound
from app.task_queue import create_worker
from app.task_queue.broker import Broker
from app.task_queue.task_store import TaskStatus


def test_broker_worker_interactions(
    task_broker: Broker, square_image: BinaryIO, not_an_image: BinaryIO
) -> None:
    """
    Test all interactions with the broker, synchronously simulating
    the behavior of the worker where necessary
    """
    worker = create_worker()

    # assert the worker has no tasks
    assert not worker._get_task()

    job_id = task_broker.add_task(square_image)
    uuid.UUID(job_id)  # Assert job_id conforms to the UUID spec

    assert task_broker.task_status(job_id) == TaskStatus.PROCESSING
    with pytest.raises(JobNotFound):
        task_broker.get_result(job_id)  # Job has not completed yet

    task = worker._get_task()
    assert task is not None

    worker._do_task(*task)
    assert task_broker.task_status(job_id) == TaskStatus.SUCCEEDED

    task_broker.get_result(job_id)  # No exception as task is succeeded now

    # Expect an error when a non-image is provided
    not_an_image_job_id = task_broker.add_task(not_an_image)
    task = worker._get_task()
    assert task is not None
    worker._do_task(*task)
    assert task_broker.task_status(not_an_image_job_id) == TaskStatus.ERROR
    # Because this job failed, this call should return a message
    assert task_broker.get_error_result(not_an_image_job_id)

    # Assert getting all results
    processing_job_id = task_broker.add_task(square_image)
    results = task_broker.get_all_results()
    assert job_id in results[TaskStatus.SUCCEEDED]
    assert not_an_image_job_id in results[TaskStatus.ERROR]
    assert processing_job_id in results[TaskStatus.PROCESSING]

    # Assert an error when providing an ID that does not correspond to a job
    with pytest.raises(JobNotFound):
        task_broker.get_result(str(uuid.uuid4()))
