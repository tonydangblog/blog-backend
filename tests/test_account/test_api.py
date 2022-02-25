"""Test Account Blueprint: APIs."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from json import loads
from pathlib import Path
from typing import Tuple

from flask import session, url_for
from pytest import mark
from werkzeug.test import Client

from app.sql import fetch_one, sql


class TestRequireLogin:
    cases = ["info_update", "update_email_frequency", "delete"]

    @mark.parametrize("endpoint", cases)
    def test_redirects_to_login_page_if_not_authenticated(
        self, client: Client, endpoint: str
    ) -> None:
        # GIVEN Test client with non-authenticated user.
        # WHEN Account blueprint endpoint is requested.
        res = client.post(
            url_for(f"account.{endpoint}"),
            headers={"Accept": "text/html"},
            follow_redirects=True,
        )
        # THEN User is redirected to login page.
        assert b"Login | Tony Dang" in res.data  # nosec


class TestInfoUpdateAPI:
    cases = [
        ("Preferred name given", {"name": "Tony", "preferred_name": "Tony"}),
        ("Preferred name not given", {"name": "Tony", "preferred_name": ""}),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, data", cases, ids=ids)
    def test_processes_valid_form(
        self,
        clear_logs: None,
        client: Client,
        authenticated_user: None,
        case_id: str,
        data: dict[str, str],
    ) -> None:
        # GIVEN cleared logs, test client, and authenticated user.
        # WHEN Valid user info is submitted for update.
        res = client.post(url_for("account.info_update"), data=data)
        # THEN User information is updated.
        contact = fetch_one("contact", "token", "sub1")
        actual = (contact["name"], contact["preferred_name"])
        assert actual == (data["name"], "Tony")  # nosec
        # AND User information update is logged.
        log = (
            Path(__file__).parents[2]
            / "logs"
            / "user_info_update"
            / "user_info_update.log"
        )
        msg = (
            "\nUser information update -\n"
            "Email: sub1@t.t\n"
            f"Name: sub1 -> {contact['name']}\n"
            f"Preferred name: sub1 -> {contact['preferred_name']}"
        )
        assert msg in log.read_text()  # nosec
        # AND Empty JSON is returned.
        assert loads(res.data) == {}  # nosec

    def test_processes_invalid_form(
        self, client: Client, authenticated_user: None
    ) -> None:
        # GIVEN Test client and authenticated user.
        # WHEN Invalid user info is submitted for update.
        res = client.post(url_for("account.info_update"))
        # THEN JSON is returned with errors.
        expected = {"name": ["Whoops, it looks like you forgot to enter your name!"]}
        assert loads(res.data) == expected  # nosec


class TestUpdateEmailFrequency:
    cases = [
        (
            "sometimes",
            {"mailing_list": "1"},
            (True, 1),
            "subscribe_to_list_1",
            "subscribe to list #1",
        ),
        (
            "rarely",
            {"mailing_list": "2"},
            (True, 2),
            "subscribe_to_list_2",
            "subscribe to list #2",
        ),
        (
            "never",
            {"mailing_list": "0"},
            (False, 1),
            "api_unsubscribe",
            "unsubscribe",
        ),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, data, expected, log_name, log_message", cases, ids=ids)
    def test_processes_valid_form(
        self,
        clear_logs: None,
        client: Client,
        authenticated_user: None,
        case_id: str,
        data: dict[str, str],
        expected: Tuple[bool, int],
        log_name: str,
        log_message: str,
    ) -> None:
        # GIVEN cleared logs, test client, and authenticated user.
        # WHEN Valid email frequency update request is posted.
        if case_id == "sometimes":
            sql("""UPDATE contact SET mailing_list_id = 2 WHERE token = 'sub1'""")
            contact = fetch_one("contact", "token", "sub1")
            assert contact["mailing_list_id"] == 2  # nosec
        res = client.post(url_for("account.update_email_frequency"), data=data)
        # THEN Email frequency is updated.
        contact = fetch_one("contact", "token", "sub1")
        actual = (contact["is_subscriber"], contact["mailing_list_id"])
        assert actual == expected  # nosec
        # AND User email frequency change is logged.
        log = Path(__file__).parents[2] / "logs" / log_name / f"{log_name}.log"
        msg = f"New API {log_message} for sub1 (sub1@t.t)"
        assert msg in log.read_text()  # nosec
        # AND Empty JSON is returned.
        assert loads(res.data) == {}  # nosec

    def test_processes_invalid_form(
        self, client: Client, authenticated_user: None
    ) -> None:
        # GIVEN Test client and authenticated user.
        # WHEN Invalid email frequency update request is posted.
        res = client.post(url_for("account.update_email_frequency"))
        # THEN JSON is returned with errors.
        expected = {"mailing_list": ["Number must be between 0 and 2."]}
        assert loads(res.data) == expected  # nosec


class TestDeleteAPI:
    def test_processes_valid_form(
        self,
        clear_logs: None,
        client: Client,
        authenticated_user: None,
    ) -> None:
        # GIVEN cleared logs, test client, and authenticated user.
        # WHEN Valid account deletion request is made.
        res = client.post(url_for("account.delete"), data={"email": "sub1@t.t"})
        # THEN User account is deleted.
        assert fetch_one("contact", "token", "sub1") is None  # nosec
        # AND User account deletion record is logged.
        log = (
            Path(__file__).parents[2]
            / "logs"
            / "account_deletion"
            / "account_deletion.log"
        )
        msg = "Account deleted for sub1 (sub1@t.t)"
        assert msg in log.read_text()  # nosec
        # AND User is logged out.
        assert session.get("_id") is None  # nosec
        # AND Empty JSON is returned.
        assert loads(res.data) == {}  # nosec
        # AND Account deletion success is flashed.
        res = client.get(url_for("main.home"))
        assert b"Your account has been successfully deleted." in res.data  # nosec

    def test_processes_invalid_form(
        self, client: Client, authenticated_user: None
    ) -> None:
        # GIVEN Test client and authenticated user.
        # WHEN Invalid account deletion request is made.
        res = client.post(url_for("account.delete"))
        # THEN JSON is returned with errors.
        expected = {"email": ["Please enter your exact email (sub1@t.t) to proceed."]}
        assert loads(res.data) == expected  # nosec
