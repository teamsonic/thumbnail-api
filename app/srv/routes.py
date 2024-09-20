from enum import StrEnum


class Routes(StrEnum):
    CHECK_JOB_STATUS = "/check_job_status/{job_id}"
    DOWNLOAD_THUMBNAIL = "/download_thumbnail/{job_id}"
    HEALTHCHECK = "/healthcheck"
    JOBS = "/jobs"
    UPLOAD_IMAGE = "/upload_image"
