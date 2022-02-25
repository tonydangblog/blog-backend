"""Test Date Module."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from datetime import date

from pytest import mark

from app.date import format_date


class TestFormatDate:
    @mark.parametrize("day", list(range(1, 32)))
    def test_formats_date_where_day_has_suffix(self, day: int) -> None:
        # GIVEN Day 1-31 and corresponding suffix.
        if 11 <= day <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

        # WHEN Date is formatted.
        actual = format_date(date(2020, 12, day), "%B {do}, %Y")

        # THEN Day in formatted string has suffix.
        assert actual == f"December {day}{suffix}, 2020"  # nosec
