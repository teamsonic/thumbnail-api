"""Entrypoint to the FastAPI application

The FastAPI application and its routes are defined here.
The server can be started with command "fastapi <path/to/this/file>"
See https://fastapi.tiangolo.com/fastapi-cli/
"""

import logging.config

import yaml
from fastapi import FastAPI, status

from app import settings
from app.srv.events import lifespan
from app.srv.handlers import (
    check_job_status_handler,
    download_thumbnail_handler,
    get_all_jobs_handler,
    healthcheck,
    upload_image_handler,
)
from app.srv.middleware import check_content_length
from app.srv.models import AllJobsModel as AllJobsModel
from app.srv.models import JobStatusModel as JobStatusModel
from app.srv.models import UploadImageModel as UploadImageModel
from app.srv.routes import Routes as Routes
from app.srv.worker_monitor import worker_monitor

# Attempt to load the logging configuration, but fall back on
# the default logger if something goes wrong.
try:
    with open(settings.log_conf_file, "rb") as f:
        logging_config = yaml.safe_load(f.read())
        logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.exception(e)

app = FastAPI(lifespan=lifespan)

# Route -> Handler mappings
app.get(
    Routes.CHECK_JOB_STATUS,
    responses={
        status.HTTP_303_SEE_OTHER: {
            "description": "Task is complete and client should fetch the resource "
            "at the location given by the 'Location' header"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No task associated with provided job id"
        },
    },
)(check_job_status_handler)

app.get(
    Routes.DOWNLOAD_THUMBNAIL,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "No thumbnail associated with provided job id"
        }
    },
)(download_thumbnail_handler)

app.get(Routes.HEALTHCHECK)(healthcheck)

app.get(Routes.JOBS)(get_all_jobs_handler)

app.post(
    Routes.UPLOAD_IMAGE,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {"description": "Image accepted for processing"},
        status.HTTP_411_LENGTH_REQUIRED: {
            "description": "Missing 'content-length' header"
        },
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {
            "description": f"Submitted content is larger than the allowed "
            f"maximum of {settings.max_file_size}"
        },
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {
            "description": "File type is not supported"
        },
    },
)(upload_image_handler)

# Middleware
app.middleware("http")(check_content_length)
