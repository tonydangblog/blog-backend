"""Rand(om) Module."""

from secrets import choice
from string import ascii_letters


def rand_str(length: int = None, charset: str = ascii_letters) -> str:
    """Return a random string.

    :param length: length of string (default 16-32 characters)
    :param charset: character set for string (default [A-Za-z])
    """
    if length is None:
        length = choice(range(16, 33))
    return "".join(choice(charset) for _ in range(length))
