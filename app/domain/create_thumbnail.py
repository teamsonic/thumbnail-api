from typing import BinaryIO

from PIL import Image

from app import settings


def create_thumbnail(image: BinaryIO) -> Image.Image:
    pil_image = Image.open(image)
    pil_image.thumbnail(settings.thumbnail_size)
    return (
        pil_image
        if pil_image.size == settings.thumbnail_size
        else _add_border_to_thumbnail(pil_image)
    )


def _add_border_to_thumbnail(thumbnail: Image.Image) -> Image.Image:
    """Add padding to a thumbnail to make its size 100x100

    :param thumbnail: The PIL Image thumbnail where the height and width are each <= 100px
    :return: A new PIL Image with the original pasted on a background to enforce a size of 100x100
    """
    result = Image.new(
        thumbnail.mode, settings.thumbnail_size, settings.thumbnail_background
    )
    box_width: int = 0
    box_height: int = 0
    if thumbnail.width < 100:
        box_width = int((100 - thumbnail.width) / 2)
    elif thumbnail.height < 100:
        box_height = int((100 - thumbnail.height) / 2)
    result.paste(thumbnail, (box_width, box_height))
    return result
