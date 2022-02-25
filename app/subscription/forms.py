"""Subscription Blueprint: Forms."""

from secrets import token_urlsafe

from app.forms import NameEmailForm
from app.sql import fetch_one
from app.stmts import insert_contact, update_contact
from app.subscription.emails import send_opt_in_email


class SubscriptionForm(NameEmailForm):
    """Mailing list subscription form."""

    def process_subscription_request(self) -> str:
        """Update/insert contact if needed and send opt-in email."""
        preferred_name = self.name.data.split()[0]
        contact = fetch_one("contact", "email", self.email.data)
        if contact:
            if contact["is_subscriber"] or contact["is_banned"]:
                return "Contact is subscriber or banned."
            if contact["is_verified"]:
                send_opt_in_email(preferred_name, contact["email"], contact["token"])
                return "Opt-in email sent."
            update_contact(self.name.data, preferred_name, contact["email"])
            send_opt_in_email(preferred_name, contact["email"], contact["token"])
            return "Contact updated, opt-in email sent."
        token = token_urlsafe()
        insert_contact(self.name.data, preferred_name, self.email.data, token)
        send_opt_in_email(preferred_name, self.email.data, token)
        return "New contact inserted, opt-in email sent."
