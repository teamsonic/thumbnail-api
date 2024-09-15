"""Entrypoint to the FastAPI application

The FastAPI application and its routes are defined here.
The server can be started with command "fastapi <path/to/this/file>"
See https://fastapi.tiangolo.com/fastapi-cli/
"""
from fastapi import FastAPI

from app.adapters.handler import healthcheck, upload_image_handler

app = FastAPI()

app.get("/healthcheck")(healthcheck)
app.post("/upload_image")(upload_image_handler)
