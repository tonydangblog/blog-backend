"""Form Filters."""

from typing import Union

from werkzeug.urls import url_parse


def filter_all_whitespace(value: Union[str, None]) -> str:
    """Strip whitespace including in between words."""
    if isinstance(value, str):
        return " ".join(value.split())
    return ""


def filter_whitespace(value: Union[str, None]) -> str:
    """Strip whitespace."""
    if isinstance(value, str):
        return value.strip()
    return ""


def filter_to_float(value: Union[str, None]) -> float:
    """Covert value to float."""
    if not value:
        return 0
    try:
        return float(value)
    except ValueError:
        return 0


def filter_to_uppercase(value: Union[str, None]) -> str:
    """Covert value to uppercase."""
    if isinstance(value, str):
        return value.upper()
    return ""


def filter_url(url: Union[str, None]) -> str:
    """Filter unsafe URL."""
    if not url or url_parse(url).netloc != "":
        return ""
    return url
