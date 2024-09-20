"""Houses all FastAPI handlers to which web requests are dispatched.

FastAPI performs dependency injection based on the handler's function signature.
See https://fastapi.tiangolo.com/tutorial/dependencies/
"""

import uuid
from typing import Any

from fastapi import HTTPException, Request, Response, UploadFile, status
from fastapi.responses import StreamingResponse

from app import settings
from app.domain.interactions.check_job_status import check_job_status
from app.domain.interactions.download_thumbnail import download_thumbnail
from app.domain.interactions.get_all_job_ids import get_all_job_ids
from app.domain.interactions.upload_image import upload_image
from app.exceptions import InvalidImage, JobNotFound
from app.srv.models import AllJobs, JobStatusModel, UploadImageModel
from app.srv.routes import Routes
from app.task_queue.task_store import TaskStatus


async def healthcheck() -> dict[str, str]:
    """Reports the availability of the application.

    :return: A dict of {"status": "healthy"}
    """
    return {"status": "healthy"}


async def upload_image_handler(
    file: UploadFile, response: Response
) -> dict[str, str | int]:
    """Handles requests to convert an image to a thumbnail.

    :param file: The uploaded file
    :param response: The response object
    :return: An UploadImageModel with the job_id of the asynchronous thumbnail
        conversion job. The Location response header will be the URL of the
        job status.
    """
    try:
        job_id = upload_image(file.file)
    except InvalidImage:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type",
        )

    response.headers["Location"] = Routes.CHECK_JOB_STATUS.format(job_id=job_id)
    return UploadImageModel(job_id=job_id).model_dump()


async def download_thumbnail_handler(job_id: str) -> StreamingResponse:
    try:
        thumbnail = download_thumbnail(job_id)
    except JobNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Completed job with ID {job_id} not found",
        )
    return StreamingResponse(
        thumbnail, media_type=f"image/{settings.thumbnail_file_type}".lower()
    )


async def check_job_status_handler(
    job_id: str, request: Request, response: Response
) -> dict[Any, Any]:
    try:
        uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="job_id must be uuid-compliant",
        )

    try:
        job_status, message = check_job_status(job_id)
    except JobNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="job not found"
        )

    if job_status == TaskStatus.SUCCEEDED:
        message = f"{request.base_url}{job_id}"
        response.headers["Location"] = Routes.DOWNLOAD_THUMBNAIL.format(job_id=job_id)
        response.status_code = status.HTTP_303_SEE_OTHER

    return JobStatusModel(status=job_status, resource_url=message).model_dump()


async def get_all_jobs_handler() -> AllJobs:
    job_ids = get_all_job_ids()
    return AllJobs(job_ids=job_ids)
