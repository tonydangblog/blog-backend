"""Error Blueprint: Emails."""

from datetime import datetime

from flask import current_app
from werkzeug.exceptions import InternalServerError

from app.email import send_email


def send_error_email(err: InternalServerError) -> str:
    """Send error notification email."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return send_email(
        recipients=current_app.config["ADMINS"],
        subject="Site Error",
        text=f"{timestamp}\n\n{err.code} - {err.name}\n{err.description}",
    )
