"""Test Base Forms Module."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from flask import url_for
from pytest import mark
from werkzeug.test import Client

from app.forms import BaseForm, EmailForm, NameEmailForm, UUIDForm
from app.rand import rand_str


class TestFormCSRFProtection:
    def test_enabled_in_non_testing_environment(self, dev_client: Client) -> None:
        # GIVEN Test client with development configuration.
        # WHEN Form validation is attempted without CSRF token.
        dev_client.post(url_for("main.home"))
        form = BaseForm()
        # THEN Form does not validate due to missing CSRF token.
        assert (  # nosec
            form.validate_on_submit(),
            "csrf_token" in form.errors,
        ) == (False, True)

    def test_disabled_in_testing_environment(self, client: Client) -> None:
        # GIVEN Test client with testing configuration.
        # WHEN Form validation is attempted without CSRF token.
        client.post(url_for("main.home"))
        form = BaseForm()
        # THEN Form does validate despite missing CSRF token.
        assert (  # nosec
            form.validate_on_submit(),
            "csrf_token" in form.errors,
        ) == (True, False)


class TestBaseForm:
    def test_filters_unsafe_next_url(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Form is instantiated with unsafe next URL.
        client.post(url_for("main.home"), data={"next_url": "https://google.com"})
        form = BaseForm()
        # THEN Form next URL is properly filtered.
        assert form.next_url.data == ""  # nosec

    def test_flashes_error(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Form is submitted with invalid data.
        res = client.post(url_for("auth.login"), follow_redirects=True)
        # THEN First form error is flashed to user.
        msg = b"Whoops, it looks like you did not enter a valid email!"
        assert msg in res.data  # nosec


class TestNameEmailForm:
    cases = [
        ("No name", {"name": "", "email": "tony@tonydang.blog"}, False),
        ("Name too long", {"name": rand_str(51), "email": "tony@tonydang.blog"}, False),
        ("No email", {"name": "Tony", "email": ""}, False),
        ("Invalid email", {"name": "Tony", "email": "t@t"}, False),
        ("Valid inputs", {"name": "Tony", "email": "tony@tonydang.blog"}, True),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, data, expected", cases, ids=ids)
    def test_validates(
        self, client: Client, case_id: str, data: dict[str, str], expected: bool
    ) -> None:
        # GIVEN Test client, POST data, and expected validation result.
        # WHEN Form instance is instantiated with POST data.
        client.post(url_for("main.home"), data=data)
        form = NameEmailForm()
        # THEN Form validates as expected.
        assert form.validate_on_submit() == expected  # nosec

    def test_filters_name_whitespace(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Form instance is instantiated with name with excess whitespace.
        client.post(url_for("main.home"), data={"name": " Tony "})
        form = NameEmailForm()
        # THEN Form filters name whitespace.
        assert form.name.data == "Tony"  # nosec

    def test_filters_email_whitespace(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Form instance is instantiated with email with excess whitespace.
        client.post(url_for("main.home"), data={"email": "  t@t   "})
        form = NameEmailForm()
        # THEN Form filters email whitespace.
        assert form.email.data == "t@t"  # nosec

    def test_sets_no_name_error_message(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Form instance is instantiated with missing name.
        client.post(url_for("main.home"), data={"name": ""})
        form = NameEmailForm()
        form.validate_on_submit()
        # THEN Correct error message is set.
        actual = form.errors["name"][0]
        assert actual == "Whoops, it looks like you forgot to enter your name!"  # nosec

    def test_sets_invalid_name_length_error_message(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Form instance is instantiated with name that is too long.
        client.post(url_for("main.home"), data={"name": rand_str(51)})
        form = NameEmailForm()
        form.validate_on_submit()
        # THEN correct error message is set.
        expected = "Whoops, the name entered must be between 1 to 50 characters."
        actual = form.errors["name"][0]
        assert actual == expected  # nosec

    def test_sets_invalid_email_error_message(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Form instance is instantiated with invalid email.
        client.post(url_for("main.home"), data={"email": "t@t"})
        form = NameEmailForm()
        form.validate_on_submit()
        # THEN correct error message is set.
        expected = "Whoops, it looks like you did not enter a valid email!"
        actual = form.errors["email"][0]
        assert actual == expected  # nosec


class TestEmailForm:
    def test_inherits_from_name_email_form_without_name_validation(
        self, client: Client
    ) -> None:
        # GIVEN Test client.
        # WHEN Form instance is instantiated with only valid email.
        client.post(url_for("main.home"), data={"email": "tony@tonydang.blog"})
        form = EmailForm()
        # THEN Form validates email.
        assert form.validate_on_submit() is True  # nosec


class TestUUIDForm:
    cases = [
        ("5d9759d5-17d5-464a-a414-914dd7906d67", True),
        ("invalid_uuid", False),
        ("", False),
    ]

    @mark.parametrize("uuid, expected", cases)
    def test_validates(self, client: Client, uuid: str, expected: bool) -> None:
        # GIVEN Test client and UUIDs.
        # WHEN Form instance is instantiated with UUID in POST data.
        client.post(url_for("main.home"), data={"uuid": uuid})
        form = UUIDForm()
        # THEN Form validates as expected.
        assert form.validate_on_submit() == expected  # nosec
