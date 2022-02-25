"""Test Error Blueprint: Emails."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from werkzeug.exceptions import InternalServerError
from werkzeug.test import Client

from app.error.emails import send_error_email
from tests.markers import skipif_sends_email


@skipif_sends_email
def test_send_error_email(client: Client) -> None:
    # GIVEN Test client for application context and an error object.
    err = InternalServerError()
    # WHEN Error email is sent.
    res = send_error_email(err)
    # THEN Asynchronous email is sent to inbox.
    assert res == "Thread started."  # nosec
