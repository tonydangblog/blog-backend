"""Account Blueprint: Forms."""

from flask_login import current_user
from wtforms.fields import EmailField, IntegerField, StringField
from wtforms.validators import Length, NumberRange, ValidationError

from app.forms import BaseForm, NameEmailForm
from app.forms.filters import filter_all_whitespace, filter_whitespace
from app.forms.msgs import length_msg


class InfoUpdateForm(NameEmailForm):
    """User info update form."""

    email = None
    preferred_name = StringField(
        validators=[Length(0, 50, length_msg("preferred name", 0, 50))],
        filters=[filter_all_whitespace],
    )

    def set_preferred_name(self) -> None:
        """Set preferred name if not given."""
        if self.name.data and not self.preferred_name.data:
            self.preferred_name.data = self.name.data.split()[0]


class EmailFrequencyForm(BaseForm):
    """Email frequency form."""

    mailing_list = IntegerField(validators=[NumberRange(0, 2)])


class DeleteForm(BaseForm):
    """Account deletion form."""

    email = EmailField(filters=[filter_whitespace])

    def validate_email(  # pylint: disable=no-self-use; WTForms pattern
        self, email: EmailField
    ) -> None:
        """Validate user entered email equals current user email."""
        if email.data != current_user.email:
            msg = f"Please enter your exact email ({current_user.email}) to proceed."
            raise ValidationError(msg)
