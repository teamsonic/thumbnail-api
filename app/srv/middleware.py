from typing import Awaitable, Callable

from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from app import settings
from app.srv.models import ErrorResponseModel


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
