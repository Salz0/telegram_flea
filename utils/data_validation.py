import mimetypes
from aiogram.types import Document


def validate_photo_as_document(file: Document) -> bool:
    """Validation of a photo uploaded as a document"""

    # checking the file extension
    photo_type = mimetypes.guess_type(file.file_name)
    if photo_type[0] is None:
        return False
    return photo_type[0].startswith("image")
