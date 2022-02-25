"""Test Render Module."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from os.path import getmtime

from flask import url_for
from werkzeug.test import Client

from app.render import static_file
from tests.markers import skipif_sends_email


class TestStaticFile:
    def test_generates_file_path_with_version(self) -> None:
        # GIVEN N/A.
        # WHEN Static file path is generated.
        path = static_file("dist/css/base.bundle.css")
        # THEN Path is generated with version.
        version = getmtime("app/static/dist/css/base.bundle.css")
        assert path == f"/static/dist/css/base.bundle.css?v={version}"  # nosec


class TestRenderHTML:
    def test_uses_passed_page_properties_if_given(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Admin page is requested by non-admin.
        headers = {"Accept": "text/html"}
        res = client.get(url_for("admin.index"), headers=headers)
        # THEN Error page properties are loaded for display instead of requested path
        #      page properties.
        assert b"Whoops | Tony Dang" in res.data  # nosec

    @skipif_sends_email
    def test_displays_admin_routes(
        self, client: Client, authenticated_admin: None
    ) -> None:
        # GIVEN Test client and authenticated admin.
        # WHEN Admin page is requested.
        res = client.get(url_for("admin.contacts"))
        # THEN Admin routes are displayed for navigation.
        actual = (b"/admin/contacts" in res.data, b"/admin/pages" in res.data)
        assert actual == (True, True)  # nosec

    def test_displays_main_routes(self, client: Client) -> None:
        # GIVEN Test client and non-admin user.
        # WHEN Non-admin page is requested.
        res = client.get(url_for("main.home"))
        # THEN Main routes are displayed for navigation.
        routes = ("/posts", "/about", "/now", "/contact", "/support")
        for route in routes:
            assert route.encode("UTF-8") in res.data  # nosec
        actual = (b"/admin/contacts" in res.data, b"/admin/pages" in res.data)
        assert actual == (False, False)  # nosec

    def test_displays_authenicated_routes(
        self, client: Client, authenticated_user: None
    ) -> None:
        # GIVEN Test client and authenticated user.
        # WHEN Any page is requested.
        res = client.get(url_for("main.home"))
        # THEN Authenticated routes are displayed for navigation.
        assert (b"sub1@t.t" in res.data, b"logout" in res.data) == (True, True)  # nosec

    def test_does_not_display_logout_when_not_authenticated(
        self, client: Client
    ) -> None:
        # GIVEN Test client and non-authenticated user.
        # WHEN Any page is requested.
        res = client.get(url_for("main.home"))
        # THEN Authenticated routes are not displayed for navigation.
        assert b"logout" not in res.data  # nosec

    def test_display_page_title_for_home_page(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Home page is requested.
        res = client.get(url_for("main.home"))
        # THEN '| Tony Dang' is not suffixed onto page title.
        assert b"| Tony Dang" not in res.data  # nosec

    def test_display_page_title_for_non_home_page(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Non-home page is requested.
        res = client.get(url_for("main.now"))
        # THEN '| Tony Dang' is suffixed onto page title.
        assert b"Now | Tony Dang" in res.data  # nosec

    def test_display_narrow_page(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Narrow page is requested.
        res = client.get(url_for("main.home"))
        # THEN Narrow class is added to main and site-footer blocks.
        actual = (b"main--narrow" in res.data, b"site-footer--narrow" in res.data)
        assert actual == (True, True)  # nosec

    @skipif_sends_email
    def test_display_non_narrow_page(
        self, client: Client, authenticated_admin: None
    ) -> None:
        # GIVEN Test client authenticated_admin.
        # WHEN Non-narrow page is requested.
        res = client.get(url_for("admin.contacts"))
        # THEN Narrow class is not added.
        assert b"main--narrow" not in res.data  # nosec
