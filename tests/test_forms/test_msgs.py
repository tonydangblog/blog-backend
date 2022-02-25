"""Test Form Error Messages."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from app.forms.msgs import email_msg, length_msg, required_msg


def test_email_msg() -> None:
    # GIVEN N/A.
    # WHEN Email error message is generated.
    # THEN Email error message is returned.
    expected = "Whoops, it looks like you did not enter a valid email!"
    assert email_msg() == expected  # nosec


def test_required_msg() -> None:
    # GIVEN Name of the required input field.
    # WHEN Required data error message is generated.
    actual = required_msg("name")
    # THEN Required data error message is returned with name of input field.
    expected = "Whoops, it looks like you forgot to enter your name!"
    assert actual == expected  # nosec


def test_length_msg() -> None:
    # GIVEN Name, max length, and min length of the input field.
    # WHEN Length error message is generated.
    actual = length_msg("name", 1, 10)
    # THEN Length error message is returned with name and min&max length of input field.
    expected = "Whoops, the name entered must be between 1 to 10 characters."
    assert actual == expected  # nosec
