from django.core.validators import RegexValidator


name_regex_validator = RegexValidator(
    r"^(?!.*\s{2,})[A-Za-z]+(?: [A-Za-z]+)*$",
    "Ensure that the name contains only English letters or spaces, with no leading or trailing spaces and no consecutive spaces."
)


key_regex_validator = RegexValidator(
    r"^[A-Z]+(?:_[A-Z]+)*$",
    "Ensure that the key contains only uppercase English letters or underscores, with no leading or trailing underscores and no consecutive underscores."
)
