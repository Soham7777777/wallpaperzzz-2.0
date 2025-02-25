from dataclasses import dataclass
from typing import ClassVar, Literal
from django.utils.deconstruct import deconstructible
from django.db.models.fields.files import FieldFile
from django.core.exceptions import ValidationError


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
