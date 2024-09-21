import asyncio
import threading

import pytest

from app.srv.worker_monitor import worker_monitor
from app.task_queue.worker import Worker


@pytest.mark.asyncio
async def test_worker_monitor() -> None:
    """Assert the behavior of worker monitor

    The worker monitor should start a worker thread and
    continue to monitor it, creating a replacement worker
    if the monitored worker ever dies.
    """
    # Start the worker monitor
    task = asyncio.create_task(worker_monitor())

    async def shutdown() -> None:
        """Cleanup function to run after assertions"""
        task.cancel()
        await asyncio.wait_for(task, timeout=5)

    async def get_worker_thread() -> Worker:
        """Function to find the running worker thread"""
        counter = 0
        while True:
            for thread in threading.enumerate():
                if thread.name.startswith("Worker"):
                    return thread  # type: ignore
            await asyncio.sleep(1)
            counter += 1
            if counter >= 5:
                raise asyncio.TimeoutError

    # Find the currently running worker
    # If no worker is found in 5 seconds, the test fails.
    worker_thread = await asyncio.create_task(get_worker_thread())

    # Send the worker an interrupt signal and wait for confirmation
    # it has died. If this does not happen in 5 seconds, the test fails
    worker_thread.interrupt()
    await asyncio.wait_for(asyncio.to_thread(worker_thread.join), timeout=5)
    assert not worker_thread.is_alive()

    # Look for another worker thread, which the worker monitor should have
    # automatically started after the death of the first worker.
    # If one cannot be found, the test fails
    worker_thread2 = await asyncio.create_task(get_worker_thread())
    assert worker_thread.name != worker_thread2.name
    assert worker_thread2.is_alive()

    # Send a cancellation signal to the worker monitor
    # and confirm it shut down the second worker before exiting
    try:
        await shutdown()
    except asyncio.CancelledError:
        assert not worker_thread2.is_alive()
