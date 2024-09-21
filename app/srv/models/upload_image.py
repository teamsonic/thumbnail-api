from pydantic import BaseModel


class UploadImageModel(BaseModel):
    """Schema for thumbnail creation API requests.

    :cvar job_id: Field to validate the job_id associated with the uploaded image.
    """

    job_id: str
