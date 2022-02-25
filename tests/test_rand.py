"""Test Rand Module."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from re import match
from string import ascii_letters, ascii_lowercase, ascii_uppercase, digits, punctuation

from pytest import mark

from app.rand import rand_str


class TestRandStr:
    def test_generates_random_string_with_no_args(self) -> None:
        # GIVEN No arguments.
        # WHEN Random string is generated.
        random_string = rand_str()
        # THEN String is between 16-32 characters and uses the [A-Za-z] character set.
        assert (  # nosec
            len(random_string) >= 16,
            len(random_string) <= 32,
            match("[^A-Za-z]", random_string),
        ) == (True, True, None)

    cases = [
        ("ascii_letters", 10, ascii_letters, "[^A-Za-z]"),
        ("ascii_lowercase", 15, ascii_lowercase, "[^a-z]"),
        ("ascii_uppercase", 20, ascii_uppercase, "[^A-Z]"),
        ("digits", 25, digits, r"[^\d]"),
        ("punctuation", 30, punctuation, r"[A-Za-z\d]"),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, length, charset, regex", cases, ids=ids)
    def test_generates_random_strings_using(
        self, case_id: str, length: int, charset: str, regex: str
    ) -> None:
        # GIVEN Length, character set, and regex.
        # WHEN Random string is generated with given length and charset.
        random_string = rand_str(length, charset)
        # THEN String is of given length and character set given.
        assert (  # nosec
            len(random_string),
            match(regex, random_string),
        ) == (length, None)
