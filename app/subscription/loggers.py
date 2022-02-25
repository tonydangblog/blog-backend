"""Subscription Blueprint: Loggers."""

from app.logging import create_logger

opt_in_logger = create_logger("opt_in")
subscription_request_logger = create_logger("subscription_request")
unsubscribe_logger = create_logger("unsubscribe")


def log_opt_in(name: str, email: str) -> None:
    """Log mailing list subscription opt-in."""
    opt_in_logger.info("New subscriber opt-in for %s (%s)", name, email)


def log_subscription_request(name: str, email: str) -> None:
    """Log mailing list subscription request."""
    subscription_request_logger.info(
        "New subscription request for %s (%s)", name, email
    )


def log_unsubscribe(name: str, email: str) -> None:
    """Log mailing list unsubscribe."""
    unsubscribe_logger.info("New unsubscribe for %s (%s)", name, email)
