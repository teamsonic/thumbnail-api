"""Houses all FastAPI handlers to which web requests are dispatched.

FastAPI performs dependency injection based on the handler's function signature.
See https://fastapi.tiangolo.com/tutorial/dependencies/
"""

import uuid
from typing import Any

from fastapi import Request, Response, UploadFile, status

from app.domain.interactions.check_job_status import check_job_status
from app.domain.interactions.upload_image import upload_image
from app.exceptions import InvalidImage, JobNotFound
from app.srv.models import ErrorResponseModel, JobStatusModel, UploadImageModel
from app.task_queue.task_store import TaskStatus


async def healthcheck() -> dict[str, str]:
    """Reports the availability of the application.

    :return: A dict of {"status": "healthy"}
    """
    return {"status": "healthy"}


async def upload_image_handler(
    file: UploadFile, response: Response
) -> dict[str, str | int]:
    """Handles requests to convert an image to a thumbnail

    :param file: The uploaded file
    :param response: The response object
    :return: An UploadImageModel with the job_id of the asynchronous thumbnail
    conversion job or an ErrorResponseModel
    """
    model: ErrorResponseModel | UploadImageModel

    try:
        job_id = upload_image(file.file)
    except InvalidImage:
        response.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        model = ErrorResponseModel(
            error="Unsupported file type", status_code=response.status_code
        )
    else:
        model = UploadImageModel(job_id=job_id)

    return model.model_dump()


async def check_job_status_handler(
    job_id: str, request: Request, response: Response
) -> dict[Any, Any]:
    model: ErrorResponseModel | JobStatusModel

    try:
        uuid.UUID(job_id)
    except ValueError:
        model = ErrorResponseModel(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="job_id must be uuid-compliant",
        )
        response.status_code = status.HTTP_400_BAD_REQUEST
        return model.model_dump()

    try:
        job_status, message = check_job_status(job_id)
    except JobNotFound:
        model = ErrorResponseModel(
            status_code=status.HTTP_404_NOT_FOUND, error="job not found"
        )
        response.status_code = status.HTTP_404_NOT_FOUND
        return model.model_dump()

    if job_status == TaskStatus.SUCCEEDED:
        message = f"{request.base_url}{job_id}"

    return JobStatusModel(status=job_status, resource_url=message).model_dump()
