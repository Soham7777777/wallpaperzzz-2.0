from django.core import validators
from django.db.models import PositiveIntegerField, BooleanField

from common.utils import ImageType


class WallpaperDimensionField(PositiveIntegerField):
    
    def __init__(self) -> None:
        super().__init__()
        self.blank = False
        self.null = False
        self.validators.append(validators.MinValueValidator(64))
        self.validators.append(validators.MaxValueValidator(4096))
