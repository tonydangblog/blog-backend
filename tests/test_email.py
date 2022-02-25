"""Test Email Module"""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from werkzeug.test import Client

from app.email import send_email
from tests.markers import skipif_sends_email


@skipif_sends_email
def test_send_email_async(client: Client) -> None:
    # GIVEN Test client for app context.
    # WHEN Asynchronous email is sent.
    res = send_email(
        recipients=["tonytadang@gmail.com"],
        subject="[test_email 1/4]async",
        text="PASSED",
    )
    # THEN Asynchronous email is sent with proper function response.
    assert res == "Thread started."  # nosec


@skipif_sends_email
def test_send_email_sync(client: Client) -> None:
    # GIVEN Test client for app context.
    # WHEN Synchronous email is sent.
    res = send_email(
        recipients=["tonytadang@gmail.com"],
        subject="[test_email 2/4]sync",
        text="PASSED",
        sync=True,
    )
    # THEN Synchronous email is sent with proper function response.
    assert res == "Sent to: ['tonytadang@gmail.com']"  # nosec


@skipif_sends_email
def test_send_email_with_custom_sender(client: Client) -> None:
    # GIVEN Test client for app context.
    # WHEN Email with custom sender is sent.
    res = send_email(
        recipients=["tonytadang@gmail.com"],
        subject="[test_email 3/4] sender",
        text="PASSED if from tony@tonydang.blog",
        sender="tony@tonydang.blog",
    )
    # THEN Email with custom sender is sent with proper function response.
    assert res == "Thread started."  # nosec


@skipif_sends_email
def test_send_email_with_html_body(client: Client) -> None:
    # GIVEN Test client for app context.
    # WHEN Email with html body is sent.
    res = send_email(
        recipients=["tonytadang@gmail.com"],
        subject="[test_email 4/4] HTML",
        text="FAILED",
        html="<h1>PASSED</h1>",
    )
    # THEN HTML email is sent with proper function response.
    assert res == "Thread started."  # nosec


def test_send_email_exception(client: Client) -> None:
    # GIVEN Test client for app context.
    # WHEN Email with invalid inputs is sent.
    res = send_email(
        recipients=[""],
        subject="",
        text="",
        sync=True,
    )
    # THEN Error message is returned.
    assert res == "Invalid email address ."  # nosec
