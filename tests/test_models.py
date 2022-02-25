"""Test App Models."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from werkzeug.test import Client

from app.models import Contact
from app.sql import fetch_one


class TestContactModel:
    def test_instantiates_contact_model(self, client: Client) -> None:
        # GIVEN Test client for app context.
        # WHEN Contact is instantiated.
        contact = Contact(fetch_one("contact", "token", "sub1"))
        # THEN Contact attributes are mapped from db and inherited from UserMixin.
        assert (  # nosec
            len(vars(contact)),
            contact.is_active,
            contact.is_authenticated,
            contact.is_anonymous,
            contact.get_id(),
        ) == (13, True, True, False, "sub1")
