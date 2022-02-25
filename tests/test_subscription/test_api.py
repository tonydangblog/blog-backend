"""Test Subscription Blueprint: APIs."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from datetime import datetime
from json import loads
from pathlib import Path

from flask import url_for
from freezegun import freeze_time
from werkzeug.test import Client

from app.sql import fetch_one
from tests.markers import skipif_sends_email


class TestSubscriptionForm:
    @skipif_sends_email
    @freeze_time(datetime.utcnow())
    def test_processes_valid_form(self, clear_logs: None, client: Client) -> None:
        # GIVEN Cleared logs and test client.
        # WHEN Valid POST request is made.
        data = {"name": "Tony D", "email": "tonytadang@gmail.com"}
        res = client.post(url_for("subscription.subscription_form"), data=data)
        # THEN Subscription request is processed.
        contact = fetch_one("contact", "email", data["email"])
        assert contact["name"] == data["name"]  # nosec
        # AND Subscription request is logged.
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log = (
            Path(__file__).parents[2]
            / "logs"
            / "subscription_request"
            / "subscription_request.log"
        )
        msg = f"New subscription request for {data['name']} ({data['email']})"
        actual = (timestamp in log.read_text(), msg in log.read_text())
        assert actual == (True, True)  # nosec
        # AND Empty JSON is returned.
        assert loads(res.data) == {}  # nosec

    def test_processes_invalid_form(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Invalid POST request is made.
        data = {"name": "", "email": "tonytadang@gmail.com"}
        res = client.post(url_for("subscription.subscription_form"), data=data)
        # THEN JSON is returned with errors.
        expected = {"name": ["Whoops, it looks like you forgot to enter your name!"]}
        assert loads(res.data) == expected  # nosec
