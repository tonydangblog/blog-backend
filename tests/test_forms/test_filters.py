"""Test Form Filters."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from pytest import mark
from werkzeug.test import Client

from app.forms.filters import (
    filter_all_whitespace,
    filter_to_float,
    filter_to_uppercase,
    filter_url,
    filter_whitespace,
)


class TestFilterAllWhitespace:
    cases = [
        ("No string", None, ""),
        ("Empty String", "", ""),
        ("String with only whitespace", " ", ""),
        ("String with two words and excess spaces", "  First  Last  ", "First Last"),
        ("String with three words and excess spaces", "  A  B  C  ", "A B C"),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, string, expected", cases, ids=ids)
    def test_filters_all_whitespace(
        self, case_id: str, string: str, expected: str
    ) -> None:
        # GIVEN String with excess whitespace.
        # WHEN Filtered.
        # THEN All excess whitespace is removed.
        assert filter_all_whitespace(string) == expected  # nosec


class TestFilterWhitespace:
    cases = [
        ("No string", None, ""),
        ("Empty string", "", ""),
        ("String with only whitespace", " ", ""),
        ("String with two words and excess spaces", "  First  Last  ", "First  Last"),
        ("String with three words and excess spaces", "  A  B  C  ", "A  B  C"),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, string, expected", cases, ids=ids)
    def test_filters_whitespace(self, case_id: str, string: str, expected: str) -> None:
        # GIVEN String with leading and trailing whitespace.
        # WHEN Filtered.
        # THEN Leading and trailing whitespace is removed.
        assert filter_whitespace(string) == expected  # nosec


class TestFilterToFloat:
    cases = [
        ("No string", None, 0),
        ("Empty string", "", 0),
        ("Integer string", "1", 1),
        ("Floating point string", "0.25", 0.25),
        ("Mixed string", "0.25F", 0),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, string, expected", cases, ids=ids)
    def test_filters_to_float(self, case_id: str, string: str, expected: str) -> None:
        # GIVEN Various strings.
        # WHEN Filtered.
        # THEN String is converted to float.
        assert filter_to_float(string) == expected  # nosec


class TestFilterToUppercase:
    cases = [
        ("No string", None, ""),
        ("Empty string", "", ""),
        ("Lowercase string", "tony", "TONY"),
        ("Title case string", "Tony", "TONY"),
        ("Uppercase string", "TONY", "TONY"),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, string, expected", cases, ids=ids)
    def test_filters_to_uppercase(
        self, case_id: str, string: str, expected: str
    ) -> None:
        # GIVEN String with with various casing.
        # WHEN Filtered.
        # THEN String is converted to uppercase.
        assert filter_to_uppercase(string) == expected  # nosec


class TestFilterUrl:
    cases = [
        ("No URL", None, ""),
        ("Empty string", "", ""),
        ("External URL", "https://google.com", ""),
        ("Valid URL #1", "/", "/"),
        ("Valid URL #2", "/now", "/now"),
        ("Valid URL #3", "/now/", "/now/"),
    ]
    ids = [f"{case[0]}: {case[1]}" for case in cases]

    @mark.parametrize("case_id, url, expected", cases, ids=ids)
    def test_filters_url(
        self, client: Client, case_id: str, url: str, expected: str
    ) -> None:
        # GIVEN Test client for application context and a URL.
        # WHEN URL is filtered.
        # THEN If safe, URL is returned as-is, else URL for app home page is returned.
        assert filter_url(url) == expected  # nosec
