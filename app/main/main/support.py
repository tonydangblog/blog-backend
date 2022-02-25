"""Main Blueprint: Support."""

from secrets import token_urlsafe
from typing import Union

import stripe
from flask import current_app, flash, redirect, render_template, request, url_for
from werkzeug import Response
from wtforms.fields import IntegerField
from wtforms.validators import NumberRange

from app import csrf
from app.email import send_email
from app.forms import BaseForm
from app.main import bp
from app.render import render_html
from app.sql import fetch_one, sql
from app.stmts import insert_contact


@bp.get("/support")
def support() -> Union[str, Response]:
    """Display Support page."""
    if request.args.get("success") == "true":
        flash(
            "Thank you for your support! 🙏 "
            "Please see your inbox for an email confirmation."
        )
        return redirect(url_for("main.support"))
    donations = sql(
        """SELECT * FROM one_time_donation ORDER BY created_at DESC""", method="all"
    )
    total_coffees = int(sum([donation["amount"] / 500 for donation in donations]))
    return render_html(
        "main/main/support/support.html",
        total_coffees=total_coffees,
        donations=donations,
        int=int,
    )


class OneTimeCheckoutForm(BaseForm):
    """One Time Checkout Form."""

    qty = IntegerField(validators=[NumberRange(1, 1000)])


@bp.post("/support/one-time/checkout")
@csrf.exempt
def support_one_time_checkout() -> Response:
    """Create Stripe checkout session for one time donation."""
    form = OneTimeCheckoutForm()
    if form.validate_on_submit():
        stripe.api_key = current_app.config["STRIPE_API_KEY"]
        checkout_session = stripe.checkout.Session.create(
            submit_type="donate",
            line_items=[
                {
                    "price": current_app.config["ONE_TIME_DONATION_PRICE"],
                    "quantity": form.qty.data,
                }
            ],
            payment_method_types=["card"],
            mode="payment",
            success_url=url_for("main.support", _external=True, success="true"),
            cancel_url=url_for("main.support", _external=True),
        )
        return redirect(checkout_session.url, code=303)
    form.flash_error()
    return redirect(url_for("main.support"))


def send_donation_confirmation_email(
    preferred_name: str, email: str, amount: int
) -> str:
    """Send donation confirmation email."""
    num_coffees = int(amount / 500)
    coffees = "1 coffee" if num_coffees == 1 else f"{num_coffees} coffees"
    amount = int(amount / 100)
    return send_email(
        recipients=[email],
        subject=f"Hi {preferred_name} - Thanks for getting me coffee!",
        text=render_template(
            "emails/support/one-time-donation-confirmation.txt",
            preferred_name=preferred_name,
            coffees=coffees,
            amount=amount,
        ),
        html=render_template(
            "emails/support/one-time-donation-confirmation.html",
            preferred_name=preferred_name,
            coffees=coffees,
            amount=amount,
        ),
    )


def handle_successful_one_time_donation(event) -> str:
    """Handle successful one time donation payment."""
    if event.type == "checkout.session.completed":
        session = stripe.checkout.Session.retrieve(
            event.data.object.id, expand=["line_items", "payment_intent"]
        )
        if (
            session.line_items.data[0].price.id
            == current_app.config["ONE_TIME_DONATION_PRICE"]
        ):
            payment_data = session.payment_intent.charges.data[0]

            name = payment_data.billing_details.name
            display_name = name.split()[0]
            email = payment_data.billing_details.email
            amount = payment_data.amount

            contact = fetch_one("contact", "email", email)
            if contact:
                contact_id = contact["contact_id"]
            else:
                insert_contact(name, display_name, email, token_urlsafe())
                contact = fetch_one("contact", "email", email)
                contact_id = contact["contact_id"]

            stmt = """
                   INSERT INTO one_time_donation (contact_id, display_name, amount)
                   VALUES (%s, %s, %s)
                   """
            sql(stmt, (contact_id, display_name, amount))
            return send_donation_confirmation_email(display_name, email, amount)
        return "Invalid product price."
    return "Invalid Event."
