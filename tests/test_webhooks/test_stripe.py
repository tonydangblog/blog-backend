"""Test Webhooks Blueprint: Stripe."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from hashlib import sha256
from hmac import new
from json import dumps
from time import time

import stripe
from flask import current_app, url_for
from werkzeug.test import Client


def mock_stripe_signature(payload: str) -> str:
    """Create mock Stripe webhook signature."""
    timestamp = int(time())
    signed_payload = f"{timestamp}.{payload}"
    signature = new(
        current_app.config["STRIPE_ENDPOINT_SECRET"].encode("UTF-8"),
        signed_payload.encode("UTF-8"),
        sha256,
    ).hexdigest()

    return f"t={timestamp},v1={signature}"


class TestStripe:
    def test_handles_invalid_payload(self, client: Client) -> None:
        # GIVEN Test client and event with invalid payload.
        stripe.api_key = current_app.config["STRIPE_API_KEY"]
        payload = ""
        signature = mock_stripe_signature(payload)

        # WHEN Event is sent to webhook listener.
        res = client.post(
            url_for("webhooks.stripe_listener"),
            data=payload,
            headers={"STRIPE_SIGNATURE": signature},
        )

        # THEN Event fails with 400 code.
        assert (res.json, res.status_code) == ({"success": False}, 400)  # nosec

    def test_handles_invalid_signature(self, client: Client) -> None:
        # GIVEN Test client and event with invalid signature.
        stripe.api_key = current_app.config["STRIPE_API_KEY"]
        payload = dumps(
            stripe.Event.retrieve(
                current_app.config["ONE_TIME_DONATION_EXISTING_CONTACT"]
            )
        )
        signature = "invalid_signature"

        # WHEN Event is sent to webhook listener.
        res = client.post(
            url_for("webhooks.stripe_listener"),
            data=payload,
            headers={"STRIPE_SIGNATURE": signature},
        )

        # THEN Event fails with 401 code.
        assert (res.json, res.status_code) == ({"success": False}, 401)  # nosec

    def test_handles_duplicate_event(self, client: Client) -> None:
        # GIVEN Test client, valid event, and mock signature.
        stripe.api_key = current_app.config["STRIPE_API_KEY"]
        payload = dumps(
            stripe.Event.retrieve(
                current_app.config["ONE_TIME_DONATION_EXISTING_CONTACT"]
            )
        )
        signature = mock_stripe_signature(payload)

        # WHEN Same event is sent to webhook listener twice.
        res = client.post(
            url_for("webhooks.stripe_listener"),
            data=payload,
            headers={"STRIPE_SIGNATURE": signature},
        )
        res = client.post(
            url_for("webhooks.stripe_listener"),
            data=payload,
            headers={"STRIPE_SIGNATURE": signature},
        )

        # THEN Event succeeds with 201 code.
        assert (res.json, res.status_code) == ({"success": True}, 201)  # nosec

    def test_handles_valid_event(self, client: Client) -> None:
        # GIVEN Test client, valid event, and mock signature.
        stripe.api_key = current_app.config["STRIPE_API_KEY"]
        payload = dumps(
            stripe.Event.retrieve(
                current_app.config["ONE_TIME_DONATION_EXISTING_CONTACT"]
            )
        )
        signature = mock_stripe_signature(payload)

        # WHEN Event is sent to webhook listener.
        res = client.post(
            url_for("webhooks.stripe_listener"),
            data=payload,
            headers={"STRIPE_SIGNATURE": signature},
        )

        # THEN Event is successfully handled.
        assert (res.json, res.status_code) == ({"success": True}, 200)  # nosec
