from django.core import validators
from django.db.models import PositiveIntegerField


class WallpaperDimensionField(PositiveIntegerField):
    
    def __init__(self) -> None:
        super().__init__()
        self.validators.append(validators.MinValueValidator(64))
        self.validators.append(validators.MaxValueValidator(8192))
