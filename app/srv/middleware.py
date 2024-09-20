from typing import Awaitable, Callable

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from app import settings


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
            return JSONResponse(
                status_code=status.HTTP_411_LENGTH_REQUIRED,
                content={"detail": "Content-Length header missing"},
            )
        elif int(content_length) > settings.max_file_size:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "File size larger than maximum limit of 5MB"},
            )
    response = await call_next(request)
    return response
