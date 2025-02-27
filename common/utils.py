from dataclasses import dataclass
from pathlib import PurePath
import string
import time
from typing import ClassVar, Literal
from django.db import models
from django.utils.deconstruct import deconstructible


@deconstructible
@dataclass
class FileUploadPathGenerator:

    base_path: PurePath
    name_prefix: str

    _name_prefix_range: ClassVar[tuple[Literal[2], Literal[16]]] = 2, 16


    def __post_init__(self) -> None:
        if self.base_path.is_absolute():
            raise ValueError(f"The base_path ({str(self.base_path)}) must be relative.")
        
        if not set(self.name_prefix).issubset(string.ascii_letters):
            raise ValueError(f"The name_prefix ({self.name_prefix}) can only contain ascii letters.")

        min_size, max_size = FileUploadPathGenerator._name_prefix_range
        if len(self.name_prefix) > max_size or len(self.name_prefix) < min_size:
            raise ValueError(f"The name_prefix ({self.name_prefix}) must be within {min_size} to {max_size} characters.")


    def __call__(self, instance: models.Model, filename_from_user: str) -> str:
        ext = PurePath(filename_from_user).suffix
        new_filename = f"{self.name_prefix}{FileUploadPathGenerator._get_timestamp()}{ext}"
        return str(self.base_path / new_filename)

    
    @staticmethod
    def _get_timestamp() -> str:
        return ''.join(str(time.time()).split('.'))
