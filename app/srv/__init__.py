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
from app.srv.handler import (
    check_job_status_handler,
    download_thumbnail_handler,
    get_all_jobs_handler,
    healthcheck,
    upload_image_handler,
)
from app.srv.middleware import check_content_length
from app.srv.worker_monitor import worker_monitor

try:
    with open(settings.log_conf_file, "rb") as f:
        logging_config = yaml.safe_load(f.read())
        logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.exception(e)
app = FastAPI(lifespan=lifespan)

app.get("/jobs")(get_all_jobs_handler)
app.get("/check_job_status/{job_id}")(check_job_status_handler)
app.get("/download_thumbnail/{job_id}")(download_thumbnail_handler)
app.get("/healthcheck")(healthcheck)
app.post("/upload_image", status_code=status.HTTP_202_ACCEPTED)(upload_image_handler)

app.middleware("http")(check_content_length)
