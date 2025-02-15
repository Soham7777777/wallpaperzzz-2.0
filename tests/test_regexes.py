import unittest
import re
import adminapp.models


class TestNameRegex(unittest.TestCase):

    regex = adminapp.models.NAME_REGEX[0]


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
                self.assertIsNotNone(re.match(self.regex, string))
            

    def test_invalid_strings(self) -> None:
        for string in self.invalid_strings:
            with self.subTest(string=string):
                self.assertIsNone(re.match(self.regex, string))
