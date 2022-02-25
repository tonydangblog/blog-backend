"""Test Mailer Blueprint: Forms."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from flask import url_for
from pytest import mark
from werkzeug.test import Client

from app.mailer.forms import MailForm
from app.sql import sql


class TestMailForm:
    cases = [
        ("Valid", "1", "CONFIRM", True),
        ("Valid", "2", "CONFIRM", True),
        ("Valid", "3", "CONFIRM", True),
        ("Invalid mailing list id", 0, "CONFIRM", False),
        ("Invalid confirmation", "3", "", False),
        ("Invalid confirmation", "3", "blah", False),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize(
        "case_id, mailing_list_id, confirmation, expected", cases, ids=ids
    )
    def test_validates(
        self,
        client: Client,
        case_id: str,
        mailing_list_id: str,
        confirmation: str,
        expected: bool,
    ) -> None:
        # GIVEN Test client, POST data, and expected validation result.
        # WHEN Form instance is instantiated with POST data.
        data = {
            "mailing_list_id": mailing_list_id,
            "confirmation": confirmation,
        }
        client.post(url_for("main.home"), data=data)
        mailing_lists = sql("""SELECT * FROM mailing_list""", method="all")
        form = MailForm()
        form.mailing_list_id.choices = [
            mailing_list["mailing_list_id"] for mailing_list in mailing_lists
        ]
        # THEN Form validates as expected.
        assert form.validate_on_submit() == expected  # nosec
