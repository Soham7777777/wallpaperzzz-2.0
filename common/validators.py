from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePath
from typing import ClassVar, Literal
from django.utils.deconstruct import deconstructible
from django.db.models.fields.files import FieldFile, ImageFieldFile
from django.core.exceptions import ValidationError
from common.utils import ImageType, get_file_extensions_for_image_type


@deconstructible
@dataclass
class MaxFileSizeValidator:

    max_file_size: int

    _max_file_size_range: ClassVar[tuple[Literal[1], Literal[100_00000]]] = 1, 100_00000


    def __post_init__(self) -> None:
        min_size, max_size = MaxFileSizeValidator._max_file_size_range
        if self.max_file_size < min_size or self.max_file_size > max_size:
            raise ValueError(f"The max_file_size ({self.max_file_size}) must be an integer value within {min_size} to {max_size}.")
        

    def __call__(self, value: FieldFile) -> None:
        if value.size > self.max_file_size:
            raise ValidationError(
                "Ensure that the file size is less than or equal to %(max_size)s bytes.",
                code='file_too_large',
                params={'max_size': str(self.max_file_size)},
            )


@deconstructible
@dataclass
class ImageTypeFileExtensionsValidator:

    image_types: Sequence[ImageType]


    def __call__(self, value: ImageFieldFile) -> None:
        extensions: list[str] = []
        for image_type in self.image_types:
            extensions += [*get_file_extensions_for_image_type(image_type)]
        
        if PurePath(value.path).suffix not in extensions:
            raise ValidationError(
                "Ensure that the image file has an extension from the supported file extensions: %(extensions)s for image types: %(image_type)s.",
                code='invalid_image_extension',
                params={'extensions': tuple(extensions), 'image_type': tuple([x.value for x in self.image_types])}
            )
