"""Test SQL Statements."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from werkzeug.test import Client

from app.sql import fetch_one
from app.stmts import insert_contact, update_contact


def test_insert_contact(client: Client) -> None:
    # GIVEN Test client for app context.
    # WHEN New contact is inserted into database.
    insert_contact("Tony Dang", "Tony", "tonytadang@gmail.com", "token")
    # THEN New contact is present in contact table.
    contact = fetch_one("contact", "email", "tonytadang@gmail.com")
    assert (  # nosec
        contact["name"],
        contact["preferred_name"],
        contact["email"],
        contact["token"],
        contact["is_verified"],
        contact["is_subscriber"],
        contact["is_banned"],
        contact["mailing_list_id"],
        contact["role_id"],
    ) == (
        "Tony Dang",
        "Tony",
        "tonytadang@gmail.com",
        "token",
        False,
        False,
        False,
        1,
        1,
    )


def test_update_contact(client: Client) -> None:
    # GIVEN Test client for app context.
    # WHEN Existing contact (identified by email) is updated.
    update_contact("New Name", "New", "sub1@t.t")
    # THEN Contact name and preferred name is updated.
    contact = fetch_one("contact", "email", "sub1@t.t")
    assert (contact["name"], contact["preferred_name"]) == ("New Name", "New")  # nosec
