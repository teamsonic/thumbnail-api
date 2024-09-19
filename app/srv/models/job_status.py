from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_serializer

from app.task_queue.task_store import TaskStatus


class JobStatusModel(BaseModel):
    """
    Schema for job status API requests
    """

    model_config = ConfigDict(populate_by_name=True)

    status: TaskStatus
    resource_url: str | None = Field(alias="error", default=None)

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        data: dict[str, Any] = {"status": self.status}
        if self.status == TaskStatus.ERROR:
            data["error"] = self.resource_url
        return data
