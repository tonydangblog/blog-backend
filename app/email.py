"""Email Module.

Wrapper for sending emails via Amazon SES in Flask.
Requires 'SES' and 'SENDER' configuration variables to be set in Flask.
"""

from threading import Thread
from typing import Union

from botocore.exceptions import ClientError
from flask import Flask, current_app

MessageType = dict[str, dict[str, Union[str, dict[str, str]]]]


def send_via_ses(sender: str, recipients: list[str], message: MessageType) -> str:
    """Send synchronous email via Amazon SES."""
    ses = current_app.config["SES"]
    try:
        response = ses.send_email(
            Source=sender,
            Destination={"ToAddresses": recipients},
            Message=message,
        )
    except ClientError as err:
        print(err.response["Error"]["Message"])
        return err.response["Error"]["Message"]
    else:
        print(f'Sent to: {recipients} (Message ID: {response["MessageId"]})')
        return f"Sent to: {recipients}"


def send_async_email(
    app: Flask, sender: str, recipients: list[str], message: MessageType
) -> None:
    """Send email with app context (to enable sending async in separate thread)."""
    with app.app_context():
        send_via_ses(sender, recipients, message)


def send_email(
    recipients: list[str],
    subject: str,
    text: str,
    html: str = None,
    sender: str = None,
    sync: bool = False,
) -> str:
    """Send email.

    :param recipients: List of recipient email(s).
    :param subject: Subject of email.
    :param text: Body text of email.
    :param html: HTML body. If None, sends as text-only email.
    :param sender: Email of sender (default app.config['SENDER']).
    :param sync: True for blocking, synchronous email. False for asynchronous email in
                 separate thread. Default is False.
    """
    sender = sender or current_app.config["SENDER"]
    charset = "UTF-8"
    message: MessageType = {
        "Subject": {"Charset": charset, "Data": subject},
        "Body": {"Text": {"Charset": charset, "Data": text}},
    }

    if html:
        message["Body"]["Html"] = {"Charset": charset, "Data": html}

    if sync:
        return send_via_ses(sender, recipients, message)

    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), sender, recipients, message),
    ).start()

    return "Thread started."
