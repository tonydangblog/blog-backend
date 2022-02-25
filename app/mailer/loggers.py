"""Mailer Blueprint: Loggers."""

from app.logging import create_logger

list_mail_logger = create_logger("list_mail")


def log_list_mail(name: str, email: str) -> None:
    """Log mail sent to mailing list contact."""
    list_mail_logger.info("Mail sent to %s (%s)", name, email)
