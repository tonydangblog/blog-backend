"""Subscription Blueprint: Emails."""

from flask import render_template, url_for

from app.email import send_email
from app.jwt import generate_jwt


def send_opt_in_email(preferred_name: str, email: str, token: str) -> str:
    """Send opt-in email for mailing list."""
    jwt = generate_jwt(86400, token=token, bp="subscription")
    url = url_for("subscription.opt_in", jwt=jwt, _external=True)
    return send_email(
        recipients=[email],
        subject=f"Hi {preferred_name} - Please verify your email",
        text=render_template(
            "emails/opt-in/opt-in.txt", preferred_name=preferred_name, url=url
        ),
        html=render_template(
            "emails/opt-in/opt-in.html", preferred_name=preferred_name, url=url
        ),
    )
