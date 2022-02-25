"""Test Auth Blueprint: Emails."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from werkzeug.test import Client

from app.auth.emails import send_login_email, send_login_notification_email
from tests.markers import skipif_sends_email


@skipif_sends_email
def test_send_login_email(client: Client) -> None:
    # GIVEN Test client for application context.
    # WHEN Login email is sent.
    res = send_login_email(
        "[test_auth_emails_1/2]login_email", "tonytadang@gmail.com", "token"
    )
    # THEN Login email is received in inbox with valid login URL.
    assert res == "Thread started."  # nosec


@skipif_sends_email
def test_send_login_notification_email(client: Client) -> None:
    # GIVEN Test client for application context.
    # WHEN Login notification email is sent.
    res = send_login_notification_email(
        "[test_auth_emails_2/2]login_notification", "tonytadang@gmail.com"
    )
    # THEN Login notification email is received in inbox.
    assert res == "Thread started."  # nosec
