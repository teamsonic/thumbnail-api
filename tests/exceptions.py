"""Custom Exceptions for test cases

ImageTooLarge - Raised when an uploaded file exceeds the maximum
acceptable Content-Length and a 413 Status Code is returned

MissingContentLength - Raised when an uploaded file's request
is missing a content-length header and a 411 Status Code is
returned
"""


class ImageTooLarge(Exception):
    """
    Raised when an uploaded file exceeds the maximum allowed size
    """


class MissingContentLength(Exception):
    """
    Raised when an HTTP request is rejected for not having the
    "content-length" header.
    """
