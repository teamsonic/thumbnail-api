import pytest

from app.domain.interactions.upload_image import create_thumbnail


@pytest.mark.parametrize("image", ["wide_image", "tall_image", "square_image"])
def test_create_thumbnail(image: str, request: pytest.FixtureRequest) -> None:
    """
    Assert that a 100x100 thumbnail is created with appropriate padding
    if necessary.

    :param image: Pytest fixture name that corresponds to an image from which a 100x100
    thumbnail will be created
    :return: None
    """
    thumbnail = create_thumbnail(request.getfixturevalue(image))
    assert thumbnail.size == (100, 100)
