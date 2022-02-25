"""Test Admin Blueprint: Initialization."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from flask import url_for
from pytest import mark
from werkzeug.test import Client

from app.sql import fetch_one
from tests.markers import skipif_sends_email


class TestListView:
    @skipif_sends_email
    def test_filters_and_sorts(self, client: Client, authenticated_admin: None) -> None:
        # GIVEN Test client with authenticated admin.
        # WHEN A list view is requested with 'filtered' and 'order_by' arguments.
        res = client.get(url_for("admin.contacts", filtered="2", order_by="name"))
        # THEN List view is filtered and sorted.
        assert (  # nosec
            b"WHERE is_verified" in res.data,
            b"ORDER BY" in res.data,
            b"ban1" in res.data,
            b"unv1" in res.data,
        ) == (True, True, False, False)


class TestBeforeRequest:
    def test_denies_non_authenticated_user(self, client: Client) -> None:
        # GIVEN Test client with anonymous user.
        # WHEN Admin view is requested.
        res = client.get(url_for("admin.index"), follow_redirects=True)
        # THEN 404 page is shown.
        assert res.status_code == 404  # nosec

    def test_denies_non_admin(self, client: Client, authenticated_user: None) -> None:
        # GIVEN Test client with authenticated non-admin user.
        # WHEN Admin view is requested.
        res = client.get(url_for("admin.index"), follow_redirects=True)
        # THEN 404 page is shown.
        assert res.status_code == 404  # nosec

    @skipif_sends_email
    def test_allows_admin(self, client: Client, authenticated_admin: None) -> None:
        # GIVEN Test client with authenticated admin.
        # WHEN Admin view is requested.
        res = client.get(url_for("admin.index"), follow_redirects=True)
        # THEN Admin view is shown.
        assert res.status_code == 200  # nosec


class TestPageProperties:
    cases = ["index", "contacts", "pages", "relay_runs"]

    @mark.parametrize("endpoint", cases)
    def test_exists_in_database(self, client: Client, endpoint: str) -> None:
        # GIVEN Test client for application context.
        # WHEN Page is fetched from database.
        # THEN Page exists.
        assert fetch_one("page", "path", url_for(f"admin.{endpoint}"))  # nosec
