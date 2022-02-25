"""Auth Blueprint: Loggers."""

from app.logging import create_logger

login_request_logger = create_logger("login_request")
login_success_logger = create_logger("login_success")
registration_logger = create_logger("registration")


def log_login_request(name: str, email: str) -> None:
    """Log user login request."""
    login_request_logger.info("Login JWT requested for %s (%s)", name, email)


def log_login_success(name: str, email: str) -> None:
    """Log user login success."""
    login_success_logger.info("New successful login for %s (%s)", name, email)


def log_registration(name: str, email: str) -> None:
    """Log user registration."""
    registration_logger.info("New registration request for %s (%s)", name, email)
