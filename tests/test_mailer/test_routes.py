"""Test Mailer Blueprint: Initialization."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from pathlib import Path

from flask import url_for
from werkzeug.test import Client

from tests.markers import skipif_sends_email


class TestBeforeRequest:
    def test_denies_non_authenticated_user(self, client: Client) -> None:
        # GIVEN Test client with anonymous user.
        # WHEN Mailer page is requested.
        res = client.get(url_for("mailer.index"), follow_redirects=True)
        # THEN 404 page is shown.
        assert res.status_code == 404  # nosec

    def test_denies_non_admin(self, client: Client, authenticated_user: None) -> None:
        # GIVEN Test client with authenticated non-admin user.
        # WHEN Mailer page is requested.
        res = client.get(url_for("mailer.index"), follow_redirects=True)
        # THEN 404 page is shown.
        assert res.status_code == 404  # nosec

    @skipif_sends_email
    def test_allows_admin(self, client: Client, authenticated_admin: None) -> None:
        # GIVEN Test client with authenticated admin.
        # WHEN Mailer page is requested.
        res = client.get(url_for("mailer.index"), follow_redirects=True)
        # THEN Mailer page is shown.
        assert res.status_code == 200  # nosec


class TestMailerIndex:
    @skipif_sends_email
    def test_processes_valid_form(
        self, clear_logs: None, client: Client, authenticated_admin: None
    ) -> None:
        # GIVEN Cleared logs, test client, and authenticated_admin.
        log = Path(__file__).parents[2] / "logs" / "list_mail" / "list_mail.log"
        assert (  # nosec
            "Mail sent to Tony Dang (tony@tonydang.blog)" not in log.read_text()
        )

        # WHEN Valid POST request is made to send mail.
        data = {"mailing_list_id": "3", "confirmation": "CONFIRM"}
        res = client.post(url_for("mailer.index"), data=data, follow_redirects=True)

        # THEN List mail is logged.
        assert "Mail sent to Tony Dang (tony@tonydang.blog)" in log.read_text()  # nosec

        # AND Success message is flashed and redirects to mailer page.
        assert (  # nosec
            b"Sending to 1 recipients... See logs." in res.data,
            b"Mailer | Tony Dang" in res.data,
        ) == (True, True)

    @skipif_sends_email
    def test_processes_invalid_form(
        self, client: Client, authenticated_admin: None
    ) -> None:
        # GIVEN Test client and authenticated_admin.

        # WHEN Invalid POST request is made to send mail.
        data = {"mailing_list_id": "3", "confirmation": "blah"}
        res = client.post(url_for("mailer.index"), data=data)

        # THEN Error message is flashed and redirects to mailer page.
        assert (  # nosec
            b"Aborted." in res.data,
            b"Mailer | Tony Dang" in res.data,
        ) == (True, True)
