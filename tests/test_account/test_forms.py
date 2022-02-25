"""Test Account Blueprint: Forms."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from flask import url_for
from pytest import mark
from werkzeug.test import Client

from app.account.forms import DeleteForm, EmailFrequencyForm, InfoUpdateForm
from app.rand import rand_str


class TestInfoUpdateForm:
    cases = [
        ("Long preferred name", {"name": "T", "preferred_name": rand_str(51)}, False),
        ("Valid preferred name", {"name": "T", "preferred_name": rand_str(50)}, True),
        ("No preferred name", {"name": "T Dang", "preferred_name": ""}, True),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, data, expected", cases, ids=ids)
    def test_set_preferred_name_class_method(
        self, client: Client, case_id: str, data: dict[str, str], expected: bool
    ) -> None:
        # GIVEN Test client, POST data, and expected validation result.
        # WHEN Form set_preferred_name method is called.
        client.post(url_for("main.home"), data=data)
        form = InfoUpdateForm()
        form.set_preferred_name()
        # THEN Preferred name is set if not given.
        expected_prefferred_name = (
            data["preferred_name"] if data["preferred_name"] else "T"
        )
        assert form.preferred_name.data == expected_prefferred_name  # nosec

    @mark.parametrize("case_id, data, expected", cases, ids=ids)
    def test_validates_preferred_name_length(
        self, client: Client, case_id: str, data: dict[str, str], expected: bool
    ) -> None:
        # GIVEN Test client, POST data, and expected validation result.
        # WHEN Form instance is instantiated with POST data.
        client.post(url_for("main.home"), data=data)
        form = InfoUpdateForm()
        # THEN Form validates as expected.
        assert form.validate_on_submit() == expected  # nosec

    def test_sets_preferred_name_length_error_message(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Form instance is instantiated with preferred name that is too long.
        client.post(
            url_for("main.home"), data={"name": "T", "preferred_name": rand_str(51)}
        )
        form = InfoUpdateForm()
        form.validate_on_submit()
        # THEN correct error message is set.
        msg = "Whoops, the preferred name entered must be between 0 to 50 characters."
        actual_msg = form.errors["preferred_name"][0]
        assert actual_msg == msg  # nosec

    def test_filters_preferred_name_whitespace(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Form instance is instantiated with preferred name with excess whitespace.
        client.post(url_for("main.home"), data={"preferred_name": " Tony  Dang   "})
        form = InfoUpdateForm()
        # THEN Form filters excess whitespace.
        assert form.preferred_name.data == "Tony Dang"  # nosec


class TestEmailFrequencyForm:
    cases = [
        ("No post data", {}, False),
        ("Empty", {"mailing_list": ""}, False),
        ("Non-number", {"mailing_list": "a"}, False),
        ("Non-integer", {"mailing_list": "1.5"}, False),
        ("< 0", {"mailing_list": "-1"}, False),
        ("> 2", {"mailing_list": "3"}, False),
        ("Mailing list #0", {"mailing_list": "0"}, True),
        ("Mailing list #1", {"mailing_list": "1"}, True),
        ("Mailing list #2", {"mailing_list": "2"}, True),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, data, expected", cases, ids=ids)
    def test_validates(
        self, client: Client, case_id: str, data: dict[str, str], expected: bool
    ) -> None:
        # GIVEN Test client.
        # WHEN Form instance is instantiated with POST data.
        client.post(url_for("main.home"), data=data)
        form = EmailFrequencyForm()
        # THEN Form validates as expected.
        assert form.validate_on_submit() == expected  # nosec


class TestDeleteForm:
    def test_filters_email_whitespace(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Form instance is instantiated with email with excess whitespace.
        client.post(url_for("main.home"), data={"email": "  t@t   "})
        form = DeleteForm()
        # THEN Form filters email whitespace.
        assert form.email.data == "t@t"  # nosec

    cases = [
        ("No email", "", False),
        ("Non-matching email", "use1@t.t", False),
        ("Matching email", "sub1@t.t", True),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, email, validation", cases, ids=ids)
    def test_validates_email(
        self,
        client: Client,
        authenticated_user: None,
        case_id: str,
        email: str,
        validation: bool,
    ) -> None:
        # GIVEN Test client and authenticated user.
        # WHEN Account deletion form is instantiated.
        client.post(url_for("main.home"), data={"email": email})
        form = DeleteForm()
        # THEN If email does not match current user email, form does not validate.
        if validation:
            error = None
        else:
            error = "Please enter your exact email (sub1@t.t) to proceed."
        actual_validation = form.validate_on_submit()
        actual_error = form.errors["email"][0] if form.errors else None
        assert (actual_validation, actual_error) == (validation, error)  # nosec
