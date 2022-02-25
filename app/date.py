"""Date Module.

Datetime helper functions.
"""

from datetime import date


def format_date(date_object: date, format_string: str) -> str:
    """date.strftime wrapper.

    :param date_object: A datetime.date object.
    :param format_string: Format string where '{do}' is placeholder for day with suffix.
    """
    if 11 <= date_object.day <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(date_object.day % 10, "th")
    day_with_suffix = f"{date_object.day}{suffix}"
    return date_object.strftime(format_string).replace("{do}", day_with_suffix)
