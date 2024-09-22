from typing import BinaryIO

from PIL import Image

from app import settings

WIDTH = settings.thumbnail_size[0]
HEIGHT = settings.thumbnail_size[1]


def create_thumbnail(image: BinaryIO) -> Image.Image:
    """Create a thumbnail from an image.

    The desired thumbnail size is provided by the global app settings.
    The thumbnail as created by the PIL library is guaranteed to
    preserve the original aspect ratio of the image using the supplied
    size as the maximum resolution. For a square image, the resulting
    thumbnail will match the provided thumbnail size.

    This function guarantees that the thumbnail will always match the app-supplied
    thumbnail size even if given an image that is not 1:1 aspect ratio. It does
    this by padding the shorter of the two dimensions.

    See https://pillow.readthedocs.io/en/stable/reference/Image.html#create-thumbnails
    :param image: File-like interface to image binary data
    :return: A PIL Image.Image object representing the thumbnail
    """
    pil_image: Image.Image = Image.open(image)
    pil_image.thumbnail(settings.thumbnail_size)
    if pil_image.size != settings.thumbnail_size:
        pil_image = _add_border_to_thumbnail(pil_image)
    return pil_image.convert("RGB")


def _add_border_to_thumbnail(thumbnail: Image.Image) -> Image.Image:
    """Add padding to a thumbnail if not a 1:1 aspect ratio.

    Non-square images will result in a non-square thumbnail smaller than the desired
    dimensions. This function adds padding as necessary to keep the aspect ratio of the
    original thumbnail while enforcing the size requirements of the thumbnail.

    The color of the padding is given by global application settings.

    :param thumbnail: A PIL Image thumbnail
    :return: A new PIL Image with padding
    """
    result = Image.new(
        thumbnail.mode, settings.thumbnail_size, settings.thumbnail_background
    )
    box_width: int = 0
    box_height: int = 0
    if thumbnail.width < WIDTH:
        box_width = int((WIDTH - thumbnail.width) / 2)
    elif thumbnail.height < HEIGHT:
        box_height = int((HEIGHT - thumbnail.height) / 2)
    result.paste(thumbnail, (box_width, box_height))
    return result
