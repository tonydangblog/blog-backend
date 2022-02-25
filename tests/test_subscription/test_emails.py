"""Test Subscription Blueprint: Emails."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from werkzeug.test import Client

from app.subscription.emails import send_opt_in_email
from tests.markers import skipif_sends_email


@skipif_sends_email
def test_send_opt_in_email(client: Client) -> None:
    # GIVEN Test client for application context.
    # WHEN Opt-in email is sent.
    res = send_opt_in_email(
        "[test_subscription_emails_1/1]opt_in", "tonytadang@gmail.com", "token"
    )
    # THEN Opt-in email is received in inbox with valid opt-in URL.
    assert res == "Thread started."  # nosec
