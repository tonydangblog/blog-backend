"""Account Blueprint: Loggers."""

from typing import Any

from app.account.forms import InfoUpdateForm
from app.logging import create_logger

account_deletion_logger = create_logger("account_deletion")
api_unsubscribe_logger = create_logger("api_unsubscribe")
subscribe_to_list_1_logger = create_logger("subscribe_to_list_1")
subscribe_to_list_2_logger = create_logger("subscribe_to_list_2")
user_info_update_logger = create_logger("user_info_update")


def log_account_deletion(name: str, email: str) -> None:
    """Log user account deletion."""
    account_deletion_logger.info("Account deleted for %s (%s)", name, email)


def log_api_unsubscribe(name: str, email: str) -> None:
    """Log user unsubscribe via API."""
    api_unsubscribe_logger.info("New API unsubscribe for %s (%s)", name, email)


def log_subscribe_to_list_1(name: str, email: str) -> None:
    """Log user subscribe to mailing list #1."""
    subscribe_to_list_1_logger.info(
        "New API subscribe to list #1 for %s (%s)", name, email
    )


def log_subscribe_to_list_2(name: str, email: str) -> None:
    """Log user subscribe to mailing list #2."""
    subscribe_to_list_2_logger.info(
        "New API subscribe to list #2 for %s (%s)", name, email
    )


def log_user_info_update(contact: Any, form: InfoUpdateForm) -> None:
    """Log user information update."""
    record_template = (
        "\nUser information update -\n"
        "Email: %s\n"
        "Name: %s -> %s\n"
        "Preferred name: %s -> %s"
    )
    user_info_update_logger.info(
        record_template,
        contact["email"],
        contact["name"],
        form.name.data,
        contact["preferred_name"],
        form.preferred_name.data,
    )
