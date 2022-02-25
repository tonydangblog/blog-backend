"""Test Account Blueprint: Routes."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from flask import url_for
from pytest import mark
from werkzeug.test import Client

from app.sql import fetch_one, sql
from app.stmts import update_contact


class TestRequireLogin:
    def test_redirects_to_login_page_if_not_authenticated(self, client: Client) -> None:
        # GIVEN Test client with non-authenticated user.
        # WHEN Account blueprint endpoint is requested.
        res = client.get(
            url_for("account.settings"),
            headers={"Accept": "text/html"},
            follow_redirects=True,
        )
        # THEN User is redirected to login page.
        assert b"Login | Tony Dang" in res.data  # nosec

    def test_allows_access_to_account_settings_page_if_authenticated(
        self, client: Client, authenticated_user: None
    ) -> None:
        # GIVEN Test client with authenticated user.
        # WHEN Account settings page is requested.
        res = client.get(url_for("account.settings"))
        # THEN User is allowed access to account settings page.
        assert b"Settings | Tony Dang" in res.data  # nosec


class TestPageProperties:
    cases = ["settings"]

    @mark.parametrize("endpoint", cases)
    def test_exists_in_database(self, client: Client, endpoint: str) -> None:
        # GIVEN Test client for application context.
        # WHEN Page is fetched from database.
        # THEN Page exists.
        assert fetch_one("page", "path", url_for(f"account.{endpoint}"))  # nosec


class TestAccountSettingsPage:
    def test_pre_populates_user_info(
        self, client: Client, authenticated_user: None
    ) -> None:
        # GIVEN Test client and authenticated user.
        update_contact("sub1_name", "sub1_preferred_name", "sub1@t.t")
        # WHEN Account settings page is requested.
        res = client.get(url_for("account.settings"))
        # THEN User name and preferred name is pre-populated.
        assert (  # nosec
            b"sub1_name" in res.data,
            b"sub1_preferred_name" in res.data,
        ) == (True, True)

    def test_checks_sometimes_option(
        self, client: Client, authenticated_user: None
    ) -> None:
        # GIVEN Test client and authenticated user on mailing list #1.
        # WHEN Account settings page is requested.
        res = client.get(url_for("account.settings"))
        # THEN Sometimes list radio button is checked.
        assert b'value="1"\n    \n      checked' in res.data  # nosec

    def test_checks_rarely_option(
        self, client: Client, authenticated_user: None
    ) -> None:
        # GIVEN Test client and authenticated user on mailing list #2.
        sql("""UPDATE contact SET mailing_list_id = 2 WHERE token = 'sub1'""")
        # WHEN Account settings page is requested.
        res = client.get(url_for("account.settings"))
        # THEN Rarely list radio button is checked.
        assert b'value="2"\n    \n      checked' in res.data  # nosec

    def test_checks_never_option(
        self, client: Client, authenticated_user: None
    ) -> None:
        # GIVEN Test client and authenticated user that is not subscribed.
        sql("""UPDATE contact SET is_subscriber = false WHERE token = 'sub1'""")
        # WHEN Account settings page is requested.
        res = client.get(url_for("account.settings"))
        # THEN Never list radio button is checked.
        assert b'value="0"\n    \n      checked' in res.data  # nosec
