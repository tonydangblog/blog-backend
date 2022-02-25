"""Test Main Blueprint: Support."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

import stripe
from flask import current_app, url_for
from pytest import mark
from werkzeug.test import Client

from app.main.main.support import (
    OneTimeCheckoutForm,
    handle_successful_one_time_donation,
    send_donation_confirmation_email,
)
from app.sql import fetch_one, sql
from tests.markers import skipif_sends_email


class TestSupport:
    def test_displays_success_message(self, client: Client) -> None:
        # GIVEN Test client.

        # WHEN Page is requested with success = true in URL arguments.
        res = client.get(url_for("main.support", success="true"), follow_redirects=True)

        # THEN Success message is flashed on support page.
        msg = (
            "Thank you for your support! 🙏 "
            "Please see your inbox for an email confirmation."
        )
        assert msg.encode("UTF-8") in res.data  # nosec
        assert b"Buy Me A Coffee?" in res.data  # nosec

    def test_displays_total_coffees_received(self, client: Client) -> None:
        # GIVEN Test client.

        # WHEN Page is requested.
        res = client.get(url_for("main.support"))

        # THEN Total coffees received count displayed.
        donations = sql("""SELECT * FROM one_time_donation""", method="all")
        total_coffees = int(sum([donation["amount"] / 500 for donation in donations]))
        msg = f"<strong>{total_coffees}</strong> &times; &#x2615; received from..."
        assert msg.encode("UTF-8") in res.data  # nosec

    def test_displays_donation_feed(self, client: Client) -> None:
        # GIVEN Test client.

        # WHEN Page is requested.
        res = client.get(url_for("main.support"))

        # THEN Donation feed is displayed.
        msg = "<strong>Mysterious Benefactor</strong> bought 1 &times; &#x2615;"
        assert msg.encode("UTF-8") in res.data  # nosec


class TestOneTimeCheckoutForm:
    cases = [
        ("No post data", {}, False),
        ("Empty qty", {"qty": ""}, False),
        ("Non-number", {"qty": "a"}, False),
        ("Non-integer", {"qty": "1.5"}, False),
        ("Qty < 1", {"qty": "-1"}, False),
        ("Qty = 0", {"qty": "0"}, False),
        ("Qty > 1000", {"qty": "1001"}, False),
        ("Valid input", {"qty": "1"}, True),
        ("Valid input", {"qty": "999"}, True),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, data, expected", cases, ids=ids)
    def test_validates(
        self, client: Client, case_id: str, data: dict[str, str], expected: bool
    ) -> None:
        # GIVEN Test client.

        # WHEN Form instance is instantiated with POST data.
        client.post(url_for("main.home"), data=data)
        form = OneTimeCheckoutForm()

        # THEN Form validates as expected.
        assert form.validate_on_submit() == expected  # nosec


class TestSupportOneTimeCheckout:
    def test_redirects_to_stripe_if_valid_checkout_qty(self, client: Client) -> None:
        # GIVEN Test client.

        # WHEN Valid post request is made.
        res = client.post(url_for("main.support_one_time_checkout"), data={"qty": 1})

        # THEN Client is redirected to Stripe.
        assert res.status_code == 303  # nosec

    def test_flashes_error_if_invalid_checkout_qty(self, client: Client) -> None:
        # GIVEN Test client.

        # WHEN Invalid post request is made.
        res = client.post(
            url_for("main.support_one_time_checkout"),
            data={"qty": 0},
            follow_redirects=True,
        )

        # THEN Error message is flashed in page.
        assert b"Number must be between 1 and 1000." in res.data  # nosec


@skipif_sends_email
def test_send_dontation_confirmation_email(client: Client) -> None:
    # GIVEN Test client for application context.

    # WHEN Confirmation email is sent.
    res = send_donation_confirmation_email(
        "[test_support_send_donation_confirmation_email]", "tonytadang@gmail.com", 500
    )
    res = send_donation_confirmation_email(
        "[test_support_send_donation_confirmation_email]", "tonytadang@gmail.com", 1000
    )

    # THEN Confirmation email is received in inbox.
    assert res == "Thread started."  # nosec


class TestHandleSuccessfulOneTimeDonation:
    def test_handles_invalid_event(self, client: Client) -> None:
        # GIVEN Invalid checkout.session.completed event.
        stripe.api_key = current_app.config["STRIPE_API_KEY"]
        event = stripe.Event.retrieve(
            current_app.config["ONE_TIME_DONATION_EXISTING_CONTACT"]
        )
        event.type = "blah"

        # WHEN Event is handled.
        res = handle_successful_one_time_donation(event)

        # THEN Handler returns "Invalid Event.".
        assert res == "Invalid Event."  # nosec

    def test_handles_invalid_product_price(self, client: Client) -> None:
        # GIVEN checkout.session.completed event with invalid product id.
        stripe.api_key = current_app.config["STRIPE_API_KEY"]
        event = stripe.Event.retrieve(
            current_app.config["ONE_TIME_DONATION_INVALID_PRODUCT_ID"]
        )

        # WHEN Event is handled.
        res = handle_successful_one_time_donation(event)

        # THEN Handler returns "Invalid product price.".
        assert res == "Invalid product price."  # nosec

    @skipif_sends_email
    def test_handles_existing_contact(self, client: Client) -> None:
        # GIVEN Valid checkout.session.completed event, existing contact, and no
        # donation by 'EXISTING'.
        stripe.api_key = current_app.config["STRIPE_API_KEY"]
        event = stripe.Event.retrieve(
            current_app.config["ONE_TIME_DONATION_EXISTING_CONTACT"]
        )
        assert fetch_one("contact", "email", "tony@tonydang.blog")  # nosec
        donation = fetch_one("one_time_donation", "display_name", "EXISTING")
        assert donation is None  # nosec

        # WHEN Event is handled.
        res = handle_successful_one_time_donation(event)

        # THEN one_time_donation is added and confirmation email is sent.
        donation = fetch_one("one_time_donation", "display_name", "EXISTING")
        actual = (donation["display_name"], donation["amount"])
        assert actual == ("EXISTING", 500)  # nosec
        assert res == "Thread started."  # nosec

    @skipif_sends_email
    def test_handles_non_existing_contact(self, client: Client) -> None:
        # GIVEN Valid checkout.session.completed event, non-existing contact, and no
        # donation by 'NON_EXISTING'.
        stripe.api_key = current_app.config["STRIPE_API_KEY"]
        event = stripe.Event.retrieve(
            current_app.config["ONE_TIME_DONATION_NON_EXISTING_CONTACT"]
        )
        assert fetch_one("contact", "email", "tonytadang@gmail.com") is None  # nosec
        donation = fetch_one("one_time_donation", "display_name", "NON_EXISTING")
        assert donation is None  # nosec

        # WHEN Event is handled.
        res = handle_successful_one_time_donation(event)

        # THEN Contact and one_time_donation is added and confirmation email is sent.
        assert fetch_one("contact", "email", "tonytadang@gmail.com")  # nosec
        donation = fetch_one("one_time_donation", "display_name", "NON_EXISTING")
        actual = (donation["display_name"], donation["amount"])
        assert actual == ("NON_EXISTING", 500)  # nosec
        assert res == "Thread started."  # nosec
