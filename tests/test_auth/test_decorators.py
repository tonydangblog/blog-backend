"""Test Auth Blueprint: Decorators."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from json import loads

from flask import url_for
from pytest import mark
from werkzeug.test import Client


class TestJSONUnauthorizedHandler:
    def test_handles_unauthorized_request(self, client: Client) -> None:
        # GIVEN Test client with anonymous user.
        # WHEN API endpoint is requested and client prefers json response.
        headers = {"Accept": "application/json"}
        res = client.post(url_for("account.update_email_frequency"), headers=headers)
        # THEN Flask-login unauthorized_handler is invoked with JSON response.
        actual = (loads(res.data), res.status_code)
        assert actual == ({"error": "Unauthorized"}, 401)  # nosec

    def test_passes_authenticated_user(
        self, client: Client, authenticated_user: None
    ) -> None:
        # GIVEN Test client with authenticated user.
        # WHEN API endpoint is requested.
        res = client.post(
            url_for("account.update_email_frequency"), data={"mailing_list": "1"}
        )
        # THEN Requested JSON is returned.
        assert loads(res.data) == {}  # nosec


class TestHTMLUnauthorizedHandler:
    cases = [
        ("Flashes error message", b"Please verify your identity to continue."),
        ("Redirects to Login page", b"Login | Tony Dang"),
        ("Remembers next_url", b"/account/settings"),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, expected", cases, ids=ids)
    def test_handles_unauthorized_request(
        self, client: Client, case_id: str, expected: bytes
    ) -> None:
        # GIVEN Test client with anonymous user and expected strings in response HTML.
        # WHEN Login_required route is requested.
        res = client.get(
            url_for("account.settings"),
            headers={"Accept": "text/html"},
            follow_redirects=True,
        )
        # THEN Flask-login unauthorized_handler is invoked.
        assert expected in res.data  # nosec

    def test_passes_authenticated_user(
        self, client: Client, authenticated_user: None
    ) -> None:
        # GIVEN Test client with authenticated user.
        # WHEN Login_required route is requested.
        res = client.get(url_for("account.settings"), follow_redirects=True)
        # THEN Requested view is shown.
        assert b"Settings | Tony Dang" in res.data  # nosec


class TestNonAuthenticatedUserOnlyDecorator:
    def test_redirects_if_authenticated(
        self, client: Client, authenticated_user: None
    ) -> None:
        # GIVEN Test client with authenticated user.
        # WHEN Non-authenticated user route is requested.
        res = client.get(url_for("auth.login"), follow_redirects=True)
        # THEN User is redirected to home page.
        assert b"Settings | Tony Dang" in res.data  # nosec

    def test_shows_view_if_not_authenticated(self, client: Client) -> None:
        # GIVEN Test client with anonymous user.
        # WHEN Non-authenticated user route is requested.
        res = client.get(url_for("auth.login"), follow_redirects=True)
        # THEN Requested page is shown.
        assert b"Login | Tony Dang" in res.data  # nosec
