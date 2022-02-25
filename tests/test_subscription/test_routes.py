"""Test Subscription Blueprint: Routes"""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from datetime import datetime
from pathlib import Path

from flask import url_for
from freezegun import freeze_time
from pytest import mark
from werkzeug.test import Client

from app.jwt import generate_jwt
from app.sql import fetch_one


class TestOptIn:
    fail = b"Sorry, it looks like this link has expired!"
    success = b"Thank you! Your email has been verified!"
    cases = [
        ("Invalid bp", "unv1", "auth", False, False, fail),
        ("Subscribed contact", "sub1", "subscription", True, True, fail),
        ("Banned contact", "ban1", "subscription", False, False, fail),
        ("Verified contact", "use1", "subscription", True, True, success),
        ("Unverified contact", "unv1", "subscription", True, True, success),
    ]
    ids = [case[0] for case in cases]

    @freeze_time(datetime.utcnow())
    @mark.parametrize(
        "case_id, token, bp, is_verified, is_subscriber, msg", cases, ids=ids
    )
    def test_opts_in_contact(
        self,
        clear_logs: None,
        client: Client,
        case_id: str,
        token: str,
        bp: str,
        is_verified: bool,
        is_subscriber: bool,
        msg: bytes,
    ):
        # GIVEN Cleared logs, test client, and opt-in JWT.
        jwt = generate_jwt(token=token, bp=bp)
        # WHEN Authentication request is made.
        res = client.get(
            url_for("subscription.opt_in", jwt=jwt),
            headers={"Accept": "text/html"},
            follow_redirects=True,
        )
        # THEN User is verified and subscribed if valid JWT and corresponding message
        #      is flashed.
        contact = fetch_one("contact", "token", token)
        redirect = b"hand-wave" if b"Thank you" in msg else b"404"
        assert (  # nosec
            contact["is_verified"],
            contact["is_subscriber"],
            msg in res.data,
            redirect in res.data,
        ) == (is_verified, is_subscriber, True, True)
        # AND If successful, opt-in record is logged.
        if b"Thank you" in msg:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            log = Path(__file__).parents[2] / "logs" / "opt_in" / "opt_in.log"
            logged_msg = (
                f"New subscriber opt-in for {contact['name']} ({contact['email']})"
            )
            actual = (timestamp in log.read_text(), logged_msg in log.read_text())
            assert actual == (True, True)  # nosec


class TestUnsubscribe:
    @freeze_time(datetime.utcnow())
    def test_unsubscribes_subscriber(self, clear_logs: None, client: Client) -> None:
        # GIVEN Cleared logs and test client.
        # WHEN Unsubscribe request is made by subscriber.
        res = client.get(
            url_for("subscription.unsubscribe", token="sub1"),  # nosec
            follow_redirects=True,
        )
        # THEN Contact is unsubscribed, success message is flashed, and user is
        #      redirected to home page.
        contact = fetch_one("contact", "token", "sub1")
        assert (  # nosec
            contact["is_subscriber"],
            b"You have been successfully unsubscribed!" in res.data,
            b"hand-wave" in res.data,
        ) == (False, True, True)
        # AND Unsubscribe record is logged.
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log = Path(__file__).parents[2] / "logs" / "unsubscribe" / "unsubscribe.log"
        logged_msg = f"New unsubscribe for {contact['name']} ({contact['email']})"
        actual = (timestamp in log.read_text(), logged_msg in log.read_text())
        assert actual == (True, True)  # nosec

    def test_unsubscribes_autheniticated_user(
        self, client: Client, authenticated_user: None
    ) -> None:
        # GIVEN Test client and authenticated user.
        # WHEN Unsubscribe request is made by authenticated user.
        res = client.get(
            url_for("subscription.unsubscribe", token="sub1"),  # nosec
            follow_redirects=True,
        )
        # THEN Contact is unsubscribed, success message is flashed, and user is
        #      redirected to account settings page.
        contact = fetch_one("contact", "token", "sub1")
        assert (  # nosec
            contact["is_subscriber"],
            b"You have been successfully unsubscribed!" in res.data,
            b"Settings | Tony Dang" in res.data,
        ) == (False, True, True)

    def test_shows_404_if_invalid_contact_token(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Unsubscribe request is made with invalid contact token.
        res = client.get(
            url_for("subscription.unsubscribe", token="blah"),  # nosec
            follow_redirects=True,
        )
        # THEN 404 page is shown.
        assert b"404" in res.data  # nosec
