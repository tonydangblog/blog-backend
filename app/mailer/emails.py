"""Mailer Blueprint: Emails."""

from flask import render_template, url_for

from app.email import send_email


def send_list_email(preferred_name: str, email: str, token: str) -> str:
    """Send email to mailing list contact."""
    unsubscribe_link = url_for("subscription.unsubscribe", token=token, _external=True)
    return send_email(
        recipients=[email],
        subject="[TEST] Blog Update",
        text=render_template(
            "emails/list/list.txt",
            preferred_name=preferred_name,
            unsubscribe_link=unsubscribe_link,
        ),
        html=render_template(
            "emails/list/list.html",
            preferred_name=preferred_name,
            unsubscribe_link=unsubscribe_link,
        ),
    )
