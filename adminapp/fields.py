from django.db import models
from django.core import validators
from django.utils.deconstruct import deconstructible


@deconstructible
class WallpaperDimensionField(models.PositiveIntegerField[int, int]):
    
    def __init__(self) -> None:
        super().__init__()
        self.blank = False
        self.null = False
        self.validators.append(validators.MinValueValidator(64))
        self.validators.append(validators.MaxValueValidator(4096))
