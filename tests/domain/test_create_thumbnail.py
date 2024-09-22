import pytest

from app import settings
from app.domain.create_thumbnail import create_thumbnail


@pytest.mark.parametrize("image", ["wide_image", "tall_image", "square_image", "webp_image", "png_image"])
def test_create_thumbnail(image: str, request: pytest.FixtureRequest) -> None:
    """
    Assert that a thumbnail is created with appropriate padding
    if necessary. Or in other words, assert that the thumbnail
    matches the requested dimensions exactly.

    :param image: Pytest fixture name that corresponds to an image from which a 100x100
    thumbnail will be created
    """
    thumbnail = create_thumbnail(request.getfixturevalue(image))
    assert thumbnail.size == settings.thumbnail_size
