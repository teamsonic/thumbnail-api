"""Entrypoint to the FastAPI application

The FastAPI application and its routes are defined here.
The server can be started with command "fastapi <path/to/this/file>"
See https://fastapi.tiangolo.com/fastapi-cli/
"""

from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response, status

from app import settings
from app.adapters.handler import healthcheck, upload_image_handler
from app.models import ErrorResponseModel

app = FastAPI()

app.get("/healthcheck")(healthcheck)
app.post("/upload_image", status_code=status.HTTP_202_ACCEPTED)(upload_image_handler)


@app.middleware("http")
async def check_content_length(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """App middleware to check the Content-Length header.

    :param request: incoming fastapi Request object
    :param call_next: Next middleware function in the chain to forward the request to
    :return: An error response if the content-length header is missing or exceeds
    the maximum allowed length, or the response returned from the next middleware otherwise.
    """
    if request.method in ["POST", "PUT"]:
        content_length = request.headers.get("content-length")
        if not content_length:
            return _return_content_length_error(
                "Missing required header 'Content-Length'",
                status.HTTP_411_LENGTH_REQUIRED,
            )
        elif int(content_length) > settings.max_file_size:
            return _return_content_length_error(
                "File size larger than maximum limit of 5MB",
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )
    response = await call_next(request)
    return response


def _return_content_length_error(error_msg: str, status_code: int) -> Response:
    error = ErrorResponseModel(error=error_msg, status_code=status_code)
    response = Response(status_code=status_code, content=error.model_dump_json())
    return response
