"""Auth Blueprint: Forms."""

from secrets import token_urlsafe

from flask import Markup, escape, url_for
from flask_wtf import RecaptchaField
from wtforms.fields import EmailField
from wtforms.validators import ValidationError

from app.auth.emails import send_login_email
from app.forms import EmailForm, NameEmailForm
from app.sql import fetch_one
from app.stmts import insert_contact, update_contact


class RegistrationForm(NameEmailForm):
    """User registration form."""

    recaptcha = RecaptchaField()

    def process_registration_request(self) -> str:
        """Update/insert contact if needed and send login email unless banned."""
        preferred_name = self.name.data.split()[0]
        contact = fetch_one("contact", "email", self.email.data)
        if contact:
            token = contact["token"]
            if contact["is_banned"]:
                return "Contact is banned."
            if contact["is_verified"]:
                send_login_email(
                    preferred_name, self.email.data, token, self.next_url.data
                )
                return "Login email sent."
            update_contact(self.name.data, preferred_name, self.email.data)
            send_login_email(preferred_name, self.email.data, token, self.next_url.data)
            return "Contact updated, login email sent."
        token = token_urlsafe()
        insert_contact(self.name.data, preferred_name, self.email.data, token)
        send_login_email(preferred_name, self.email.data, token, self.next_url.data)
        return "New contact inserted, login email sent."


class LoginForm(EmailForm):
    """User login form."""

    recaptcha = RecaptchaField()

    def validate_email(self, email: EmailField) -> None:
        """Validate contact exists and is verified."""
        contact = fetch_one("contact", "email", email.data)
        if not contact or not contact["is_verified"]:
            url = url_for(
                "auth.register",
                next_url=escape(self.next_url.data),
                email=escape(email.data),
            )
            msg = Markup(
                "Whoops, no account found. Would you like to "
                f'<a href="{url}">register</a>?'
            )
            raise ValidationError(msg)
