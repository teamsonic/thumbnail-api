"""Houses all FastAPI handlers to which web requests are dispatched.

FastAPI performs dependency injection based on the handler's function signature.
See https://fastapi.tiangolo.com/tutorial/dependencies/
"""

from fastapi import UploadFile

from app.domain.interactions.upload_image import upload_image
from app.models import UploadImageModel


async def healthcheck() -> dict[str, str]:
    """Reports the availability of the application.

    :return: A dict of {"status": "healthy"}
    """
    return {"status": "healthy"}


async def upload_image_handler(file: UploadFile) -> dict[str, str]:
    job_id = upload_image(file.file)
    return UploadImageModel(job_id=job_id).model_dump()