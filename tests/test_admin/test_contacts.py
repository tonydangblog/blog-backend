"""Test Admin Blueprint: Contacts."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from flask import url_for
from werkzeug.test import Client

from app.sql import fetch_one
from tests.markers import skipif_sends_email


class TestContactListView:
    @skipif_sends_email
    def test_shows_contacts(self, client: Client, authenticated_admin: None) -> None:
        # GIVEN Test client with authenticated admin.
        # WHEN Admin contacts page is requested.
        res = client.get(url_for("admin.contacts"))
        # THEN Admin contacts page is shown.
        assert b"SELECT * FROM contact" in res.data  # nosec


class TestBanContact:
    @skipif_sends_email
    def test_bans_contact_given_valid_email(
        self, client: Client, authenticated_admin: None
    ) -> None:
        # GIVEN Test client with authenticated admin.
        # WHEN POST request is made to ban contact.
        data = {
            "next_url": "/admin/contacts",
            "uuid": "47460c72-38ee-4fd3-84bb-292ad0db77b3",
        }
        res = client.post(
            url_for("admin.ban_contact"), data=data, follow_redirects=True
        )
        # THEN Contact is banned, success message is flashed, and redirected to admin.
        contact = fetch_one("contact", "token", "sub1")
        assert (  # nosec
            contact["is_verified"],
            contact["is_subscriber"],
            contact["is_banned"],
        ) == (False, False, True)
        actual = (b"Contact banned." in res.data, b"Contacts | Tony Dang" in res.data)
        assert actual == (True, True)  # nosec

    @skipif_sends_email
    def test_shows_form_errors(self, client: Client, authenticated_admin: None) -> None:
        # GIVEN Test client with authenticated admin.
        # WHEN POST Request is made to ban contact with invalid UUID.
        data = {"next_url": "/admin/contacts", "uuid": ""}
        res = client.post(
            url_for("admin.ban_contact"), data=data, follow_redirects=True
        )
        # THEN Error message is flashed.
        assert b"Invalid UUID." in res.data  # nosec
