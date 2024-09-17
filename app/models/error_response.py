from pydantic import BaseModel


class ErrorResponseModel(BaseModel):
    """
    Schema for error responses
    """

    error: str
    status_code: int
