from pydantic import BaseModel


class AllJobsModel(BaseModel):
    """Defines schema for response to a request to get all job ids

    :cvar job_ids: Field validating and storing a list of job ids
    """

    job_ids: list[str]
