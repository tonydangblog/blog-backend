"""Subscription Blueprint: Routes."""

from flask import abort, flash, redirect, url_for
from flask_login import current_user
from werkzeug.wrappers import Response

from app.jwt import decode_jwt
from app.sql import fetch_one, sql
from app.subscription import bp
from app.subscription.loggers import log_opt_in, log_unsubscribe


@bp.get("/verify/<jwt>")
def opt_in(jwt: str) -> Response:
    """Verify mailing list subscription if valid JWT."""
    payload = decode_jwt(jwt)
    if payload and payload.get("bp") == "subscription":
        contact = fetch_one("contact", "token", payload.get("token", ""))
        if contact and not contact["is_subscriber"] and not contact["is_banned"]:
            stmt = """
                   UPDATE contact
                   SET is_verified = true, is_subscriber = true
                   WHERE email = %s
                   """
            sql(stmt, (contact["email"],))
            log_opt_in(contact["name"], contact["email"])
            flash("Thank you! Your email has been verified!")
            return redirect(url_for("main.home"))
    flash("Sorry, it looks like this link has expired!")
    return abort(404)


@bp.get("/unsubscribe/<token>")
def unsubscribe(token: str) -> Response:
    """Process unsubscribe request."""
    contact = fetch_one("contact", "token", token)
    if contact and contact["is_subscriber"]:
        stmt = """UPDATE contact SET is_subscriber = false WHERE email = %s"""
        sql(stmt, (contact["email"],))
        log_unsubscribe(contact["name"], contact["email"])
        flash("You have been successfully unsubscribed!")
        if current_user.is_authenticated:
            return redirect(url_for("account.settings"))
        return redirect(url_for("main.home"))
    return abort(404)
