from pydantic import BaseModel


class UploadImageModel(BaseModel):
    """
    Schema for thumbnail creation API requests.
    """

    job_id: str
