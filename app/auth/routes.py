"""Auth Blueprint: Routes."""

from typing import Union

from flask import abort, flash, redirect, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.wrappers import Response

from app.auth import bp
from app.auth.decorators import non_authenticated_user_only
from app.auth.emails import send_login_email, send_login_notification_email
from app.auth.forms import LoginForm, RegistrationForm
from app.auth.loggers import log_login_request, log_login_success, log_registration
from app.jwt import decode_jwt
from app.models import Contact
from app.render import render_html
from app.sql import fetch_one, sql


@bp.route("/login", methods=("GET", "POST"))
@non_authenticated_user_only
def login() -> Union[str, Response]:
    """Show user login form and process login requests."""
    form = LoginForm()
    if form.validate_on_submit():
        contact = fetch_one("contact", "email", form.email.data)
        send_login_email(
            contact["preferred_name"],
            contact["email"],
            contact["token"],
            form.next_url.data,
        )
        log_login_request(contact["name"], contact["email"])
        flash("Success! Please check your email for a link to sign in!")
        return redirect(url_for("auth.login", next_url=form.next_url.data))
    form.flash_error()
    next_url = form.next_url.data or request.args.get("next_url", "")
    return render_html(
        "auth/login/login.html",
        form=form,
        next_url=next_url,
        url=url_for("auth.register", next_url=next_url),
        url_text="Register",
    )


@bp.route("/register", methods=("GET", "POST"))
@non_authenticated_user_only
def register() -> Union[str, Response]:
    """Show user registration form and process registration requests."""
    form = RegistrationForm()
    if form.validate_on_submit():
        form.process_registration_request()
        log_registration(form.name.data, form.email.data)
        flash(
            "Thank you for registering. "
            "Please check your email for a link to sign in!"
        )
        return redirect(url_for("auth.register", next_url=form.next_url.data))
    form.flash_error()
    next_url = form.next_url.data or request.args.get("next_url", "")
    return render_html(
        "auth/register/register.html",
        form=form,
        next_url=next_url,
        url=url_for("auth.login", next_url=next_url),
        url_text="Login",
    )


@bp.get("/authenticate/<jwt>")
@non_authenticated_user_only
def authenticate(jwt: str) -> Response:
    """Verify user registration if valid token and log in user."""
    payload = decode_jwt(jwt)
    if payload and payload.get("bp") == "auth":
        contact = fetch_one("contact", "token", payload.get("token", ""))
        if contact and not contact["is_banned"]:
            stmt = """UPDATE contact SET is_verified = true WHERE email = %s"""
            sql(stmt, (contact["email"],))
            login_user(Contact(contact))
            flash(f"Hi {contact['preferred_name']} - You are now logged in!")
            if contact["role_id"] == 2:
                send_login_notification_email(contact["name"], contact["email"])
            log_login_success(contact["name"], contact["email"])
            next_url = payload.get("next_url")
            if not next_url or url_parse(next_url).netloc != "":
                next_url = url_for("account.settings")
            return redirect(next_url)
    flash("Sorry, it looks like this link has expired!")
    return abort(404)


@bp.get("/logout")
def logout() -> Response:
    """Log out user."""
    if current_user.is_authenticated:
        flash("You have been successfully logged out!")
    logout_user()
    return redirect(url_for("auth.login"))
