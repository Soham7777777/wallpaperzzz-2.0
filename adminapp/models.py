from django.db import models
from django.core import validators


NAME_REGEX = r"^(?!.*\s{2,})[A-Za-z]+(?: [A-Za-z]+)*$", "The name can only contain English latters or spaces, with no leading or trailing spaces and no consecutive spaces."


class Category(models.Model):
    name = models.CharField(
        blank=False,
        null=False,
        unique=True, 
        max_length=32,
        validators=[
            validators.MinLengthValidator(2),
            validators.RegexValidator(*NAME_REGEX)
        ],
    )

