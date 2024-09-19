from pydantic import BaseModel


class AllJobs(BaseModel):
    job_ids: list[str]
