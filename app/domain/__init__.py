"""Package containing all domain logic for the application.

"Domain logic" is the solution to the essential complexity of the system, or
in other words, the inherent problem(s) the application was created to solve.

See https://en.wikipedia.org/wiki/No_Silver_Bullet

Exports:

interactions - a submodule of functionality that implements the core interaction
    logic between the application and clients.
create_thumbnail - function that accepts image data and generates a thumbnail version
check_job_status - Get the status of a job by job_id
download_thumbnail - Get the completed thumbnail by job_id
get_all_job_ids - Get a list of the ids corresponding to all jobs
    of any status
upload_image - Submit an image for thumbnail processing
"""

from app.domain.create_thumbnail import create_thumbnail as create_thumbnail
from app.domain.interactions import check_job_status as check_job_status
from app.domain.interactions import download_thumbnail as download_thumbnail
from app.domain.interactions import get_all_job_ids as get_all_job_ids
from app.domain.interactions import upload_image as upload_image
