"""Test App Initialization."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from base64 import b64encode
from pathlib import Path

from flask import url_for
from werkzeug.test import Client

from app import load_contact
from app.models import Contact
from app.sql import fetch_one


class TestHTTPAuth:
    def test_restricts_access_for_development(self, dev_client: Client) -> None:
        # GIVEN Test client with development configuration settings.
        # WHEN App is requested.
        res = dev_client.get(url_for("main.home"))
        # THEN Access is denied.
        assert res.status_code == 401  # nosec

    def test_denies_invalid_credentials(self, dev_client: Client) -> None:
        # GIVEN Test client with development configuration settings.
        # WHEN App is requested with invalid credentials.
        credentials = b64encode(b"admin:passer").decode("UTF-8")
        res = dev_client.get(
            url_for("main.home"), headers={"Authorization": f"Basic {credentials}"}
        )
        # THEN Access is denied.
        assert res.status_code == 401  # nosec

    def test_authenticates_valid_credentials(self, dev_client: Client) -> None:
        # GIVEN Test client with development configuration settings.
        # WHEN App is requested with valid credentials.
        credentials = b64encode(b"admin:pass").decode("UTF-8")
        res = dev_client.get(
            url_for("main.home"), headers={"Authorization": f"Basic {credentials}"}
        )
        # THEN Access is granted.
        assert res.status_code == 200  # nosec

    def test_does_not_restrict_access_for_testing(self, client: Client) -> None:
        # GIVEN Test client with testing configuration settings.
        # WHEN App is requested without credentials.
        res = client.get(url_for("main.home"))
        # THEN Access is granted.
        assert res.status_code == 200  # nosec


class TestFlaskLoginUserLoader:
    def test_returns_contact_object_given_valid_token(self, client: Client) -> None:
        # GIVEN Test client for app context.
        # WHEN Contact is loaded with valid token.
        contact = load_contact("adm1")
        # THEN Contact object is returned.
        assert contact == Contact(fetch_one("contact", "token", "adm1"))  # nosec

    def test_returns_none_given_invalid_token(self, client: Client) -> None:
        # GIVEN Test client for app context.
        # WHEN Contact is loaded with invalid token.
        # THEN None is returned.
        assert load_contact("") is None  # nosec


class TestLogging:
    def test_logs_request(self, clear_logs: None, client: Client) -> None:
        # GIVEN Cleared logs and test client with initial GET request made to app.
        # WHEN Request is made to app via the test client.
        # THEN Request is logged.
        log = Path(__file__).parents[1] / "logs" / "request" / "request.log"
        assert "werkzeug" in log.read_text()  # nosec

    def test_logs_app_messages(self, clear_logs: None, client: Client) -> None:
        # GIVEN Cleared logs and test client.
        # WHEN App has been created.
        # THEN App log records are recorded.
        log = Path(__file__).parents[1] / "logs" / "app" / "app.log"
        assert "Server started" in log.read_text()  # nosec
