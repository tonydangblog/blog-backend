"""Mailer Blueprint: Forms."""

from wtforms.fields import SelectField, StringField
from wtforms.validators import ValidationError

from app.forms import BaseForm


class MailForm(BaseForm):
    """Mail confirmation form."""

    mailing_list_id = SelectField()
    confirmation = StringField()

    def validate_confirmation(  # pylint: disable=no-self-use; WTForms pattern
        self, confirmation: StringField
    ) -> None:
        """Validate confirmation."""
        if confirmation.data != "CONFIRM":
            raise ValidationError("Aborted.")
