"""Custom Exceptions for the application

Exports:

InvalidImage - Raised when a provided file is not an image type
"""


class InvalidImage(Exception):
    """
    Raised when a provided file is not an image type
    """


class JobNotFound(Exception):
    """
    Raised when the status or results of a job is queried
    with a job_id that could not be found.
    """
