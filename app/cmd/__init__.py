"""Entrypoint to the FastAPI application

The FastAPI application and its routes are defined here.
The server can be started with command "fastapi <path/to/this/file>"
See https://fastapi.tiangolo.com/fastapi-cli/
"""

from fastapi import FastAPI, status

from app.cmd.handler import healthcheck, upload_image_handler
from app.cmd.middleware import check_content_length

app = FastAPI()

app.get("/healthcheck")(healthcheck)
app.post("/upload_image", status_code=status.HTTP_202_ACCEPTED)(upload_image_handler)

app.middleware("http")(check_content_length)
