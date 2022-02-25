"""Base App Forms.

Common app forms, error messages, and filters added on top of Flask-WTF.
"""

from flask import flash
from flask_wtf import FlaskForm
from wtforms.fields import EmailField, HiddenField, StringField
from wtforms.validators import UUID, DataRequired, Email, Length

from app.forms.filters import filter_all_whitespace, filter_url, filter_whitespace
from app.forms.msgs import email_msg, length_msg, required_msg


class BaseForm(FlaskForm):
    """Base form class."""

    next_url = HiddenField(filters=[filter_url])

    def flash_error(self) -> None:
        """Flash first form error."""
        if self.errors and "recaptcha" not in self.errors:
            flash(next(iter(self.errors.values()))[0])


class NameEmailForm(BaseForm):
    """Base name and email form class."""

    name = StringField(
        validators=[
            DataRequired(required_msg("name")),
            Length(1, 50, length_msg("name", 1, 50)),
        ],
        filters=[filter_all_whitespace],
    )
    email = EmailField(validators=[Email(email_msg())], filters=[filter_whitespace])


class EmailForm(NameEmailForm):
    """Base email form class."""

    name = None


class UUIDForm(BaseForm):
    """Base UUID form class."""

    uuid = HiddenField(validators=[UUID()])
