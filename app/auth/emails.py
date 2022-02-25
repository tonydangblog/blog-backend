"""Auth Blueprint: Emails."""

from datetime import datetime

from flask import current_app, render_template, url_for

from app.email import send_email
from app.jwt import generate_jwt


def send_login_email(
    preferred_name: str, email: str, token: str, next_url: str = None
) -> str:
    """Send email to user with URL for login."""
    jwt = generate_jwt(token=token, next_url=next_url, bp="auth")
    url = url_for("auth.authenticate", jwt=jwt, _external=True)
    return send_email(
        recipients=[email],
        subject=f"Hi {preferred_name} - Sign into your account",
        text=render_template(
            "emails/login/login.txt", preferred_name=preferred_name, url=url
        ),
        html=render_template(
            "emails/login/login.html", preferred_name=preferred_name, url=url
        ),
    )


def send_login_notification_email(name: str, email: str) -> str:
    """Send new successful login notification email."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return send_email(
        recipients=current_app.config["ADMINS"],
        subject="New Successful Login",
        text=f"{timestamp}\n\nName: {name}\nEmail: {email}",
    )
