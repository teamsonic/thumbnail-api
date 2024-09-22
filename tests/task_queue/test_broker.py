import uuid
from typing import BinaryIO

import pytest
from pytest import FixtureRequest

from app.domain import create_thumbnail
from app.exceptions import JobNotFound
from app.task_queue import Broker, TaskStatus, Worker, task_store

@pytest.mark.e2e
class TestFileSystemBrokerWorkerInteractions:
    """
    Test that the broker and worker correctly communicate
    with the task store and that the broker returns
    the correct responses to job status.

    The order of test methods in this class matter.
    """

    completed_job_ids: list[str]
    processing_job_ids: list[str]
    failed_job_ids: list[str]
    worker: Worker
    broker: Broker

    @classmethod
    def setup_class(cls) -> None:
        task_store.reset()
        cls.completed_job_ids = []
        cls.processing_job_ids = []
        cls.failed_job_ids = []
        cls.broker = Broker(task_store)
        cls.worker = Worker(task_store, create_thumbnail)

    @classmethod
    def teardown_class(cls) -> None:
        task_store.reset()

    @pytest.mark.parametrize("image", ["square_image", "webp_image", "png_image"])
    def test_broker_worker_interactions(
        self,
        image: str,
        request: FixtureRequest,
    ) -> None:
        """
        Test behavior when submitting supported image types
        to the broker to be converted to a thumbnail.
        """
        # assert the worker has no tasks
        assert not self.worker._get_task()

        image_fixture = request.getfixturevalue(image)
        job_id = self.broker.add_task(image_fixture)
        self.completed_job_ids.append(job_id)
        uuid.UUID(job_id)  # Assert job_id conforms to the UUID spec

        assert self.broker.task_status(job_id) == TaskStatus.PROCESSING
        with pytest.raises(JobNotFound):
            self.broker.get_result(job_id)

        task = self.worker._get_task()
        assert task is not None

        self.worker._do_task(*task)
        assert self.broker.task_status(job_id) == TaskStatus.SUCCEEDED

        # This will raise an Exception if there is no result to fetch.
        self.broker.get_result(job_id)


    def test_error(self, not_an_image: BinaryIO) -> None:
        """
        Test behavior when submitting an invalid file type, which
        is that an error message should be returned and the task
        should be placed in TaskStatus.ERROR state.

        An Exception should be raised if a job status is requested
        for a job that does not exist.
        """
        not_an_image_job_id = self.broker.add_task(not_an_image)
        self.failed_job_ids.append(not_an_image_job_id)

        task = self.worker._get_task()
        assert task is not None
        with pytest.raises(Exception):
            self.worker._do_task(*task)

        assert self.broker.task_status(not_an_image_job_id) == TaskStatus.ERROR
        # Because this job failed, this call should return a message
        assert self.broker.get_error_result(not_an_image_job_id)

        # Assert an error when providing an ID that does not correspond to a job
        with pytest.raises(JobNotFound):
            self.broker.get_result(str(uuid.uuid4()))


    def test_get_all_results(self, square_image: BinaryIO) -> None:
        """
        Test behavior when asking the broker for all job_ids.

        This test builds on the previous two.
        """
        # Assert getting all results
        processing_job_id = self.broker.add_task(square_image)
        self.processing_job_ids.append(processing_job_id)
        results = self.broker.get_all_results()
        assert set(self.completed_job_ids) == set(results[TaskStatus.SUCCEEDED])
        assert set(self.failed_job_ids) == set(results[TaskStatus.ERROR])
        assert set(self.processing_job_ids) == set(results[TaskStatus.PROCESSING])
