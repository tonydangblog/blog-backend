"""Test Mailer Blueprint: Emails."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from werkzeug.test import Client

from app.mailer.emails import send_list_email
from tests.markers import skipif_sends_email


@skipif_sends_email
def test_send_list_email(client: Client) -> None:
    # GIVEN Test client for application context.
    # WHEN List email is sent.
    res = send_list_email(
        "[test_mailer_emails_1/1]list_email", "tonytadang@gmail.com", "token"
    )
    # THEN List email is received in inbox with unsubscribe link.
    assert res == "Thread started."  # nosec
