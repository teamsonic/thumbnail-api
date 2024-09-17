"""Pydantic models for data validation and serialization

See https://docs.pydantic.dev/latest/concepts/models/

Exports:

ErrorResponseModel - Defines schema for error responses
UploadImageModel - Defines schema for response to a request to create a thumbnail
"""

from app.models.error_response import ErrorResponseModel as ErrorResponseModel
from app.models.upload_image import UploadImageModel as UploadImageModel
