from typing import BinaryIO, Protocol


class UploadImage(Protocol):
    """
    A protocol describing the interface for uploading an image.
    """

    def upload(self, file: BinaryIO) -> dict[str, str]: ...


def upload_image_specification(image_uploader: UploadImage) -> None:
    with open("日本電波塔.jpg", "rb") as f:
        response = image_uploader.upload(f)
        if "id" not in response:
            raise Exception(f"Expected key 'id' not found in {response}")
