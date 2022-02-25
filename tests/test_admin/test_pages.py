"""Test Admin Blueprint: Pages."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from flask import url_for
from werkzeug.test import Client

from tests.markers import skipif_sends_email


class TestPageListView:
    @skipif_sends_email
    def test_shows_pages(self, client: Client, authenticated_admin: None) -> None:
        # GIVEN Test client with authenticated admin.
        # WHEN Admin pages page is requested.
        res = client.get(url_for("admin.pages"))
        # THEN Admin pages page is shown.
        assert b"SELECT * FROM page" in res.data  # nosec
