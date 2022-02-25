"""Initialize App."""

from typing import Optional, Type

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash

from app.logging import create_file_handler, create_logger
from app.models import Contact
from app.sql import fetch_one
from config import Config

http_auth = HTTPBasicAuth()
login_manager = LoginManager()
csrf = CSRFProtect()


@http_auth.verify_password
def verify_password(username: str, password: str) -> Optional[str]:
    """Verify HTTP basic authentication credentials."""
    http_auth_user = fetch_one("http_auth_user", "username", username)
    if http_auth_user and check_password_hash(
        http_auth_user["password_hash"], password
    ):
        return username
    return None


@login_manager.user_loader
def load_contact(token: str) -> Optional[Contact]:
    """Contact loader for flask-login."""
    contact = fetch_one("contact", "token", token)
    if contact:
        return Contact(contact)
    return None


def create_app(config: Type[Config]) -> Flask:
    """Return Flask app instance."""
    app = Flask(__name__)
    app.config.from_object(config)
    login_manager.init_app(app)
    csrf.init_app(app)
    request_logger = create_logger("request")

    if app.debug and not app.testing:

        @app.before_request
        @http_auth.login_required
        def before_request() -> None:
            request_logger.info(None)

    else:

        @app.before_request
        def before_request() -> None:
            request_logger.info(None)

    from app import (
        account,
        admin,
        auth,
        error,
        mailer,
        main,
        sandbox,
        subscription,
        webhooks,
    )

    app.register_blueprint(account.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(error.bp)
    app.register_blueprint(mailer.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(sandbox.bp)
    app.register_blueprint(subscription.bp)
    app.register_blueprint(webhooks.bp)
    app.logger.addHandler(create_file_handler("app"))
    app.logger.setLevel("INFO")
    app.logger.info("Server started 🚀")
    return app
