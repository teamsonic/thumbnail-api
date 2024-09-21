from pydantic import BaseModel, ConfigDict, Field, model_serializer

from app.task_queue.task_store import TaskStatus


class JobStatusModel(BaseModel):
    """Schema for job status API requests

    :cvar status: Field validating the task's status
    :cvar resource_url: Field validating a message related
        to the task's status. During serialization, this field
        will become the "error" key in the response JSON if
        the task's status is TaskStatus.ERROR. Otherwise, it
        will contain the URL to the resource created by the task.
    """

    model_config = ConfigDict(populate_by_name=True)

    status: TaskStatus
    resource_url: str | None = Field(alias="error", default=None)

    @model_serializer
    def serialize_model(self) -> dict[str, str | None]:
        """Defines custom serialization logic for the entire model.

        See https://docs.pydantic.dev/latest/api/functional_serializers/#pydantic.functional_serializers.model_serializer

        The effect of this custom serializer is changing the "resource_url" field name
        to "error" if the task status is in error and an error message is being returned.

        :return: dict representing the serialized model
        """
        data: dict[str, str | None] = {"status": self.status}
        if self.status == TaskStatus.ERROR:
            data["error"] = self.resource_url
        return data
