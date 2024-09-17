"""Houses all FastAPI handlers to which web requests are dispatched.

FastAPI performs dependency injection based on the handler's function signature.
See https://fastapi.tiangolo.com/tutorial/dependencies/
"""

from fastapi import Response, UploadFile, status

from app.domain.interactions.upload_image import upload_image
from app.exceptions import InvalidImage
from app.models import ErrorResponseModel, UploadImageModel


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
