"""Test Subscription Blueprint: Forms."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from flask import url_for
from pytest import mark
from werkzeug.test import Client

from app.sql import fetch_one, sql
from app.subscription.forms import SubscriptionForm
from tests.markers import skipif_sends_email


class TestSubscriptionForm:
    cases = [
        (
            "Splits name into preferred name",
            (False, False, False),
            {"name": "[test_sub_forms_1/4] name", "email": "tonytadang@gmail.com"},
            ("[test_sub_forms_1/4]", "New contact inserted, opt-in email sent."),
        ),
        (
            "Subscribed contact",
            (True, True, False),
            {"name": "Name", "email": "tony@tonydang.blog"},
            ("Tony", "Contact is subscriber or banned."),
        ),
        (
            "Banned contact",
            (False, False, True),
            {"name": "Name", "email": "tony@tonydang.blog"},
            ("Tony", "Contact is subscriber or banned."),
        ),
        (
            "Verified contact",
            (True, False, False),
            {"name": "[test_sub_forms_2/4]verified", "email": "tony@tonydang.blog"},
            ("Tony", "Opt-in email sent."),
        ),
        (
            "Unverified contact",
            (False, False, False),
            {"name": "[test_sub_forms_3/4]unverified", "email": "tony@tonydang.blog"},
            ("[test_sub_forms_3/4]unverified", "Contact updated, opt-in email sent."),
        ),
        (
            "Non-exiting contact",
            (False, False, False),
            {"name": "[test_sub_forms_4/4]new", "email": "tonytadang@gmail.com"},
            ("[test_sub_forms_4/4]new", "New contact inserted, opt-in email sent."),
        ),
    ]
    ids = [case[0] for case in cases]

    @skipif_sends_email
    @mark.parametrize("case_id, values, data, expected", cases, ids=ids)
    def test_processes_registration_request(
        self,
        client: Client,
        case_id: str,
        values: tuple[bool, bool, bool],
        data: dict[str, str],
        expected: tuple[str, str],
    ) -> None:
        # GIVEN Test client and subscribed/banned/verified/unverified/new users.
        stmt = """
               UPDATE contact
               SET is_verified = %s, is_subscriber = %s, is_banned = %s
               WHERE email = 'tony@tonydang.blog'
               """
        sql(stmt, values)
        # WHEN Subscription request is processed.
        client.post(url_for("main.home"), data=data)
        res = SubscriptionForm().process_subscription_request()
        # THEN User is updated/inserted if applicable and proper response received.
        contact = fetch_one("contact", "email", data["email"])
        assert (contact["preferred_name"], res) == expected  # nosec
