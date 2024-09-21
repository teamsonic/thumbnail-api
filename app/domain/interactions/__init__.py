"""Package containing code that describes the core interactions of the app and its users

Exports
-------
check_job_status - Get the status of a job by job_id
download_thumbnail - Get the completed thumbnail by job_id
get_all_job_ids - Get a list of the ids corresponding to all jobs
    of any status
upload_image - Submit an image for thumbnail processing
"""

from app.domain.interactions.check_job_status import (
    check_job_status as check_job_status,
)
from app.domain.interactions.download_thumbnail import (
    download_thumbnail as download_thumbnail,
)
from app.domain.interactions.get_all_job_ids import get_all_job_ids as get_all_job_ids
from app.domain.interactions.upload_image import upload_image as upload_image
