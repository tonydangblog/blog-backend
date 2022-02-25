"""Test Error Blueprint: Handlers."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from datetime import datetime
from json import loads
from pathlib import Path

from flask import current_app, url_for
from freezegun import freeze_time
from pytest import mark
from werkzeug.test import Client

from app.error.handlers import json_error_response, prefers_json
from app.sql import fetch_one
from tests.markers import skipif_sends_email


class TestPrefersJSON:
    cases = [
        ("No MIME Types", {}, True),
        ("JSON", {"Accept": "application/json"}, True),
        ("HTML", {"Accept": "text/html"}, False),
        ("Both JSON & HTML", {"Accept": "text/html, application/json"}, True),
        ("HTML preferred", {"Accept": "text/html, application/json;q=0.9"}, False),
        ("JSON preferred", {"Accept": "text/html;q=0.9, application/json"}, True),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, headers, expected", cases, ids=ids)
    def test_returns_if_json_is_preferred(
        self, client: Client, case_id: str, headers: dict[str, str], expected: bool
    ) -> None:
        # GIVEN Test client.
        # WHEN Request is made with various accepted MIME types.
        client.get(url_for("main.home"), headers=headers)
        # THEN prefers_json returns whether JSON is preferred.
        assert prefers_json() == expected  # nosec


class TestJSONErrorResponse:
    cases = [
        (400, "Bad Request"),
        (404, "Not Found"),
        (500, "Internal Server Error"),
        (1000, "Unknown Error"),
    ]

    @mark.parametrize("status_code, message", cases)
    def test_returns_json_error(self, status_code: int, message: str) -> None:
        # GIVEN N/A.
        # WHEN JSON error response is created.
        res = json_error_response(status_code, message)
        # THEN Expected response is returned.
        assert res == ({"error": message, "message": message}, status_code)  # nosec

    def test_returns_json_error_without_message(self) -> None:
        # GIVEN N/A.
        # WHEN JSON error response is created without message.
        res = json_error_response(400)
        # THEN Expected response is returned.
        assert res == ({"error": "Bad Request"}, 400)  # nosec


class TestErrorResponse:
    def test_returns_json_error_if_preferred(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Non-existing endpoint is requested and json is preferred.
        headers = {"Accept": "application/json"}
        res = client.get("/not_existing_page", headers=headers)
        # THEN JSON error response is returned.
        json = {"error": "Not Found", "message": "404 - Whoops, resource not found..."}
        assert (loads(res.data), res.status_code) == (json, 404)  # nosec
        # AND Error is flashed on next request.
        res = client.get(url_for("main.home"))
        assert b"404 - Whoops, resource not found..." in res.data  # nosec

    def test_has_page_properties(self, client: Client) -> None:
        # GIVEN Test client for application context.
        # WHEN Error page is fetched.
        # THEN Error page exists in database.
        assert fetch_one("page", "path", "/error/whoops")  # nosec

    def test_returns_html_error(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Non-existing endpoint is requested and json is preferred.
        headers = {"Accept": "text/html"}
        res = client.get("/not_existing_page", headers=headers)
        # THEN Error page is rendered with error code.
        assert b"404 - Whoops, resource not found..." in res.data  # nosec
        # AND Error code is returned.
        assert res.status_code == 404  # nosec

    def test_error_page_properties_overrides_requested_page_properties(
        self, client: Client
    ) -> None:
        # GIVEN Test client.
        # WHEN Admin page is requested by non-admin.
        headers = {"Accept": "text/html"}
        res = client.get(url_for("admin.index"), headers=headers)
        # THEN Error page properties are loaded for display instead of requested path
        #      page properties.
        assert b"Whoops | Tony Dang" in res.data  # nosec


class TestNotFoundErrorHandler:
    def test_renders_404_page(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Non-existing page is requested.
        res = client.get("/not_existing_page")
        # THEN 404 page is shown.
        actual = (res.status_code, b"404 - Whoops, resource not found..." in res.data)
        assert actual == (404, True)  # nosec


class TestInternalServerErrorHandler:
    @skipif_sends_email
    def test_renders_500_page_and_sends_notification_email(
        self, client: Client
    ) -> None:
        # GIVEN Test client.
        # WHEN Internal server error is raised.
        res = client.get(url_for("error.internal_server_error"))
        # THEN 500 page is shown.
        actual = (res.status_code, b"500 - Whoops, something went wrong..." in res.data)
        assert actual == (500, True)  # nosec

    def test_renders_404_if_not_testing(self, client: Client) -> None:
        # GIVEN Test client with testing set to False.
        current_app.config["TESTING"] = False
        # WHEN Internal server error endpoint is requested.
        res = client.get(url_for("error.internal_server_error"))
        # THEN 404 page is shown.
        assert (res.status_code, b"404" in res.data) == (404, True)  # nosec


class TestCSRFErrorHandler:
    def test_renders_csrf_error_page(self, dev_client: Client) -> None:
        # GIVEN Test client with non-testing configuration.
        # WHEN POST request is made without CSRF token.
        res = dev_client.post(url_for("auth.login"))
        # THEN Invalid CSRF token page is shown.
        actual = (res.status_code, b"400 - Invalid CSRF token." in res.data)
        assert actual == (400, True)  # nosec

    @freeze_time(datetime.utcnow())
    def test_logs_csrf_error(self, clear_logs: None, dev_client: Client) -> None:
        # GIVEN Cleared logs and test client with non-testing configuration.
        # WHEN POST request is made without CSRF token.
        dev_client.post(url_for("auth.login"))
        # THEN CSRF error is logged.
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log = Path(__file__).parents[2] / "logs" / "csrf" / "csrf.log"
        msg = "Message: 400 - Bad Request\nThe CSRF token is missing."
        actual = (timestamp in log.read_text(), msg in log.read_text())
        assert actual == (True, True)  # nosec
