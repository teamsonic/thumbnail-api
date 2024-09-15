import uuid

from pydantic import BaseModel, field_serializer


class UploadImageModel(BaseModel):
    """
    Schema for thumbnail creation API requests.
    """
    job_id: uuid.UUID

    @field_serializer('job_id')
    def serialize_job_id(self, val: uuid.UUID) -> str:
        """

        :param val: The model's job_id value
        :return: The job_id coerced to a string
        """
        return str(val)