"""Webhooks Blueprint: Stripe."""

from typing import Dict, Tuple

import stripe
from flask import current_app, request

from app import csrf
from app.main.main.support import handle_successful_one_time_donation
from app.sql import fetch_one, sql
from app.webhooks import bp


@bp.post("/stripe")
@csrf.exempt
def stripe_listener() -> Tuple[Dict[str, bool], int]:
    """Listen for and handle webhooks from Stripe."""
    stripe.api_key = current_app.config["STRIPE_API_KEY"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            request.data,
            request.headers.get("STRIPE_SIGNATURE"),
            current_app.config["STRIPE_ENDPOINT_SECRET"],
        )
    except ValueError:
        # Invalid payload
        return {"success": False}, 400
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return {"success": False}, 401

    # Check if duplicate event.
    stripe_event = fetch_one("stripe_event", "stripe_event_id", event.id)
    if stripe_event:
        return {"success": True}, 201
    sql("""INSERT INTO stripe_event (stripe_event_id) VALUES (%s)""", (event.id,))

    # Handle valid event.
    handle_successful_one_time_donation(event)
    return {"success": True}, 200
