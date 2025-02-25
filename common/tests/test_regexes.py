from django.test import SimpleTestCase
from common.regexes import name_regex_validator, key_regex_validator
from django.core.exceptions import ValidationError


class TestNameRegex(SimpleTestCase):

    valid_strings = [
        "Hello World",
        "HelloWorld",
        "Python Regex Test"
    ]

    invalid_strings = [
        " Hello World",
        "Hello  World",
        "Hello World ", 
        "Hello    World",
        "  HelloWorld",
    ]


    def test_valid_strings(self) -> None:
        for string in self.valid_strings:
            with self.subTest(string=string):
                name_regex_validator(string)
            

    def test_invalid_strings(self) -> None:
        for string in self.invalid_strings:
            with self.subTest(string=string):
                with self.assertRaisesMessage(ValidationError, "Ensure that the name contains only English letters or spaces, with no leading or trailing spaces and no consecutive spaces."):
                    name_regex_validator(string)


class TestStringValidation(SimpleTestCase):

    valid_strings = [
        "HELLO",
        "HELLO_WORLD",
        "A_B_C_D",
    ]

    invalid_strings = [
        "hello",
        "_HELLO",
        "HELLO_",
        "HELLO__WORLD",
        "H_ELLO__WORLD",
        "H_ELLO___WORLD",
        "H_ELLO_WORL__D",
        "HELLO123",
        "HELLO WORLD",
        "",
    ]


    def test_valid_strings(self) -> None:
        for string in self.valid_strings:
            with self.subTest(string=string):
                key_regex_validator(string)
            

    def test_invalid_strings(self) -> None:
        for string in self.invalid_strings:
            with self.subTest(string=string):
                with self.assertRaisesMessage(ValidationError, "Ensure that the key contains only uppercase English letters or underscores, with no leading or trailing underscores and no consecutive underscores."):
                    key_regex_validator(string)
