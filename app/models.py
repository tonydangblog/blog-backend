"""App Models."""

from typing import Union

from flask_login import UserMixin


class Contact(UserMixin):
    """Contact model."""

    def __init__(self, contact: dict[str, Union[int, float, bool, str]]) -> None:
        """Initialize contact attributes."""
        for key, value in contact.items():
            setattr(self, key, value)
        # Set contact token as id for flask-login get_id method
        self.id = contact["token"]  # pylint: disable=invalid-name
