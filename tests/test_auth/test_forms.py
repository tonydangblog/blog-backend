"""Test Auth Blueprint: Forms."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from typing import Union

from flask import Markup, url_for
from pytest import mark
from werkzeug.test import Client

from app.auth.forms import LoginForm, RegistrationForm
from app.sql import fetch_one, sql
from tests.markers import skipif_sends_email


class TestRegistrationForm:
    cases = [
        (
            "Splits name into preferred name",
            (False, False, False),
            {"name": "[test_auth_forms_1/4] name", "email": "tonytadang@gmail.com"},
            ("[test_auth_forms_1/4]", "New contact inserted, login email sent."),
        ),
        (
            "Banned contact",
            (False, False, True),
            {"name": "Name", "email": "tony@tonydang.blog"},
            ("Tony", "Contact is banned."),
        ),
        (
            "Verified contact",
            (True, True, False),
            {"name": "[test_auth_forms_2/4]verified", "email": "tony@tonydang.blog"},
            ("Tony", "Login email sent."),
        ),
        (
            "Unverified contact",
            (False, False, False),
            {"name": "[test_auth_forms_3/4]unverified", "email": "tony@tonydang.blog"},
            ("[test_auth_forms_3/4]unverified", "Contact updated, login email sent."),
        ),
        (
            "Non-exiting contact",
            (False, False, False),
            {"name": "[test_auth_forms_4/4]new", "email": "tonytadang@gmail.com"},
            ("[test_auth_forms_4/4]new", "New contact inserted, login email sent."),
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
        # GIVEN Test client and banned/verified/unverified/new users.
        stmt = """
               UPDATE contact
               SET is_verified = %s, is_subscriber = %s, is_banned = %s
               WHERE email = 'tony@tonydang.blog'
               """
        sql(stmt, values)
        # WHEN User registration request is made.
        client.post(url_for("main.home"), data=data)
        res = RegistrationForm().process_registration_request()
        # THEN User is updated/inserted if applicable and proper response received.
        contact = fetch_one("contact", "email", data["email"])
        assert (contact["preferred_name"], res) == expected  # nosec


def error_msg(validation: bool, email: str) -> Union[None, str]:
    """Return login form error."""
    if validation:
        return None
    url = url_for("auth.register", next_url="/now", email=email)
    return Markup(
        f'Whoops, no account found. Would you like to <a href="{url}">register</a>?'
    )


class TestLoginForm:
    cases = [
        ("Banned email", "ban1@t.t", False),
        ("Verified email", "use1@t.t", True),
        ("Subscribed email", "sub1@t.t", True),
        ("Unverified email", "unv1@t.t", False),
        ("Non-existing email", "t@t.t", False),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, email, validation", cases, ids=ids)
    def test_validates_email(
        self, client: Client, case_id: str, email: str, validation: bool
    ) -> None:
        # GIVEN Test client and login email.
        # WHEN Login form is instantiated.
        client.post(url_for("main.home"), data={"next_url": "/now", "email": email})
        form = LoginForm()
        # THEN If email does not exist or is not verified, form does not validate.
        expected = (validation, error_msg(validation, email))
        actual_validation = form.validate_on_submit()
        actual_error = form.errors["email"][0] if form.errors else None
        assert (actual_validation, actual_error) == expected  # nosec
