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


class TestStringValidation(unittest.TestCase):

    regex = adminapp.models.KEY_REGEX[0]


    def _is_valid_string(self, s: str) -> bool:
        return bool(re.fullmatch(self.regex, s))


    def test_valid_strings(self) -> None:
        self.assertTrue(self._is_valid_string("HELLO"))
        self.assertTrue(self._is_valid_string("HELLO_WORLD"))
        self.assertTrue(self._is_valid_string("A_B_C_D"))
    

    def test_invalid_strings(self) -> None:
        self.assertFalse(self._is_valid_string("hello"))
        self.assertFalse(self._is_valid_string("_HELLO"))
        self.assertFalse(self._is_valid_string("HELLO_"))
        self.assertFalse(self._is_valid_string("HELLO__WORLD"))
        self.assertFalse(self._is_valid_string("H_ELLO__WORLD"))
        self.assertFalse(self._is_valid_string("H_ELLO___WORLD"))
        self.assertFalse(self._is_valid_string("H_ELLO_WORL__D"))
        self.assertFalse(self._is_valid_string("HELLO123"))
        self.assertFalse(self._is_valid_string("HELLO WORLD"))
        self.assertFalse(self._is_valid_string(""))
