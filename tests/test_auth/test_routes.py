"""Test Auth Blueprint: Routes"""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from datetime import datetime
from pathlib import Path
from time import sleep

from flask import url_for
from flask_login import current_user
from freezegun import freeze_time
from pytest import mark
from werkzeug.test import Client

from app.jwt import generate_jwt
from app.sql import fetch_one
from app.stmts import insert_contact, update_contact
from tests.markers import skipif_sends_email


class TestRedirectAuthenticatedUser:
    cases = ["login", "register", "authenticate"]

    @mark.parametrize("endpoint", cases)
    def test_redirects_if_logged_in(
        self, client: Client, authenticated_user: None, endpoint: str
    ) -> None:
        # GIVEN Test client and authenticated user.
        # WHEN Authenticated user only endpoint is requested.
        res = client.get(url_for(f"auth.{endpoint}", jwt="jwt"), follow_redirects=True)
        # THEN User is redirected to account settings page.
        assert b"Settings | Tony Dang" in res.data  # nosec


class TestPageProperties:
    cases = ["login", "register"]

    @mark.parametrize("endpoint", cases)
    def test_exists_in_database(self, client: Client, endpoint: str) -> None:
        # GIVEN Test client for application context.
        # WHEN Page is fetched from database.
        # THEN Page exists.
        assert fetch_one("page", "path", url_for(f"auth.{endpoint}"))  # nosec


class TestLoginViewFunction:
    def test_shows_login_page_on_get_request(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN GET request with next_url as argument is made for login page.
        res = client.get(url_for("auth.login", next_url="/sticky_url"))
        # THEN Login page is shown with next_url populated in form.
        actual = (b"Login | Tony Dang" in res.data, b"/sticky_url" in res.data)
        assert actual == (True, True)  # nosec

    @skipif_sends_email
    @freeze_time(datetime.utcnow())
    def test_processes_valid_form(self, clear_logs: None, client: Client) -> None:
        # GIVEN Cleared logs, test client, and verified user email.
        update_contact("Tony", "[test_auth_routes_1/2]login", "tony@tonydang.blog")
        data = {"next_url": "/sticky_url", "email": "tony@tonydang.blog"}
        # WHEN POST request is made for login.
        res = client.post(url_for("auth.login"), data=data, follow_redirects=True)
        # THEN Login request is logged.
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log = Path(__file__).parents[2] / "logs" / "login_request" / "login_request.log"
        msg = f"Login JWT requested for Tony ({data['email']})"
        assert (  # nosec
            timestamp in log.read_text(),
            msg in log.read_text(),
        ) == (True, True)
        # AND Success message is flashed and user is redirected to login page with
        #     sticky URL.
        assert (  # nosec
            b"Success! Please check your email for a link to sign in!" in res.data,
            b"Login | Tony Dang" in res.data,
            b"/sticky_url" in res.data,
        ) == (True, True, True)

    def test_processes_invalid_form(self, client: Client) -> None:
        # GIVEN Test client and invalid user email.
        data = {"next_url": "/sticky_url", "email": "t@t"}
        # WHEN POST request is made for login.
        res = client.post(url_for("auth.login"), data=data)
        # THEN Error message is flashed and login page is shown with sticky form data.
        assert (  # nosec
            b"Whoops, it looks like you did not enter a valid email!" in res.data,
            b"Login | Tony Dang" in res.data,
            b"/sticky_url" in res.data,
            b"t@t" in res.data,
        ) == (True, True, True, True)


class TestRegisterViewFunction:
    def test_shows_registration_page_on_get_request(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN GET request with next_url & email as arguments is made for registration
        #      page.
        res = client.get(
            url_for("auth.register", next_url="/sticky_url", email="sticky_email")
        )
        # THEN Registration page is shown with next_url and email populated in form.
        assert (  # nosec
            b"Register | Tony Dang" in res.data,
            b"/sticky_url" in res.data,
            b"sticky_email" in res.data,
        ) == (True, True, True)

    @skipif_sends_email
    @freeze_time(datetime.utcnow())
    def test_processes_valid_form(self, clear_logs: None, client: Client) -> None:
        # GIVEN Cleared logs, test client, and valid user registration information.
        insert_contact("Tony", "Tony", "tonytadang@gmail.com", "token")
        data = {
            "next_url": "/sticky_url",
            "name": "[test_auth_routes_2/2]register",
            "email": "tonytadang@gmail.com",
        }
        # WHEN POST request is made to register.
        res = client.post(url_for("auth.register"), data=data, follow_redirects=True)
        # THEN Registration is processed.
        contact = fetch_one("contact", "email", "tonytadang@gmail.com")
        assert contact["name"] == data["name"]  # nosec
        # AND Registration request is logged.
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log = Path(__file__).parents[2] / "logs" / "registration" / "registration.log"
        msg = f"New registration request for {data['name']} ({data['email']})"
        assert (  # nosec
            timestamp in log.read_text(),
            msg in log.read_text(),
        ) == (True, True)
        # AND Success message is flashed and user is redirected to registration page
        #     with sticky URL.
        flashed_msg = (
            b"Thank you for registering. Please check your email for a link to sign in!"
        )
        assert (  # nosec
            flashed_msg in res.data,
            b"Register | Tony Dang" in res.data,
            b"/sticky_url" in res.data,
        ) == (True, True, True)

    def test_processes_invalid_form(self, client: Client) -> None:
        # GIVEN Test client and invalid user registration information.
        data = {"next_url": "/sticky_url", "name": "sticky_name", "email": "t@t"}
        # WHEN POST request is made to register.
        res = client.post(url_for("auth.register"), data=data)
        # THEN Error message is flashed and registration page is shown with sticky data.
        assert (  # nosec
            b"Whoops, it looks like you did not enter a valid email!" in res.data,
            b"Register | Tony Dang" in res.data,
            b"/sticky_url" in res.data,
            b"sticky_name" in res.data,
            b"t@t" in res.data,
        ) == (True, True, True, True, True)


class TestAuthenticateEndpoint:
    fail = b"Sorry, it looks like this link has expired!"
    success = b"Hi unv1 - You are now logged in!"
    cases = [
        ("Show 404 on invalid JWT", 1, "unv1", "auth", "/", False, b"404"),
        ("Flashes error message on invalid JWT", 1, "unv1", "auth", "/", False, fail),
        ("Invalid bp", 600, "unv1", "subscription", "/", False, fail),
        ("Banned contact", 600, "ban1", "auth", "/", False, fail),
        ("Flashes success", 600, "unv1", "auth", "/", True, success),
        ("Admin login", 600, "adm1", "auth", "", True, b"Settings |"),
        ("Redirects per next URL", 600, "use1", "auth", "/now", True, b"Now | Tony"),
        ("Unsafe URL", 600, "sub1", "auth", "https://google.com", True, b"Settings |"),
    ]
    ids = [case[0] for case in cases]

    @skipif_sends_email
    @mark.parametrize(
        "case_id, expires_in, token, bp, next_url, authenticated, msg", cases, ids=ids
    )
    def test_authenicates_login(
        self,
        client: Client,
        case_id: str,
        expires_in: int,
        token: str,
        bp: str,
        next_url: str,
        authenticated: bool,
        msg: bytes,
    ):
        # GIVEN Test client and login JWT.
        jwt = generate_jwt(expires_in, token=token, bp=bp, next_url=next_url)
        # WHEN Authentication request is made.
        if "JWT" in case_id:
            sleep(2)
        res = client.get(
            url_for("auth.authenticate", jwt=jwt),
            headers={"Accept": "text/html"},
            follow_redirects=True,
        )
        # THEN User is authenticated if valid JWT and corresponding message is flashed.
        contact = fetch_one("contact", "token", token)
        assert (  # nosec
            contact["is_verified"],
            current_user.is_authenticated,
            msg in res.data,
        ) == (authenticated, authenticated, True)

    @freeze_time(datetime.utcnow())
    def test_logs_successful_login(self, clear_logs: None, client: Client) -> None:
        # GIVEN Cleared logs, test client, and valid login JWT.
        jwt = generate_jwt(token="unv1", bp="auth")  # nosec
        # WHEN Authentication request is made.
        client.get(url_for("auth.authenticate", jwt=jwt))
        # THEN Successful login is logged.
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log = Path(__file__).parents[2] / "logs" / "login_success" / "login_success.log"
        msg = "New successful login for unv1 (unv1@t.t)"
        assert (  # nosec
            timestamp in log.read_text(),
            msg in log.read_text(),
        ) == (True, True)


class TestLogoutViewFunction:
    def test_logs_out_user(self, client: Client, authenticated_user: None) -> None:
        # GIVEN Test client and authenticated user.
        assert current_user.is_authenticated  # nosec
        # WHEN Logout route is requested.
        res = client.get(url_for("auth.logout"), follow_redirects=True)
        # THEN Success message is flashed and user is logged out and redirected.
        assert (  # nosec
            b"You have been successfully logged out!" in res.data,
            current_user.is_authenticated,
            b"Login | Tony Dang" in res.data,
        ) == (True, False, True)
