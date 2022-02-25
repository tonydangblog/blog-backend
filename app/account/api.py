"""Account Blueprint: APIs."""

from flask import flash
from flask_login import current_user, fresh_login_required, logout_user

from app.account import bp
from app.account.forms import DeleteForm, EmailFrequencyForm, InfoUpdateForm
from app.account.loggers import (
    log_account_deletion,
    log_api_unsubscribe,
    log_subscribe_to_list_1,
    log_subscribe_to_list_2,
    log_user_info_update,
)
from app.sql import fetch_one, sql
from app.stmts import update_contact


@bp.post("/info-update")
@fresh_login_required
def info_update() -> dict:
    """Update user info."""
    form = InfoUpdateForm()
    if form.validate_on_submit():
        form.set_preferred_name()
        contact = fetch_one("contact", "email", current_user.email)
        update_contact(form.name.data, form.preferred_name.data, current_user.email)
        log_user_info_update(contact, form)
        return {}
    return form.errors


@bp.post("/update-email-frequency")
@fresh_login_required
def update_email_frequency() -> dict:
    """Update email frequency of authenticated user."""
    form = EmailFrequencyForm()
    if form.validate_on_submit():
        if form.mailing_list.data == 0:
            stmt = """UPDATE contact SET is_subscriber = false WHERE email = %s"""
            sql(stmt, (current_user.email,))
            log_api_unsubscribe(current_user.name, current_user.email)
            return {}
        if form.mailing_list.data == 1:
            stmt = """
                   UPDATE contact SET is_subscriber = true, mailing_list_id = 1
                   WHERE email = %s
                   """
            sql(stmt, (current_user.email,))
            log_subscribe_to_list_1(current_user.name, current_user.email)
            return {}
        if form.mailing_list.data == 2:
            stmt = """
                   UPDATE contact SET is_subscriber = true, mailing_list_id = 2
                   WHERE email = %s
                   """
            sql(stmt, (current_user.email,))
            log_subscribe_to_list_2(current_user.name, current_user.email)
            return {}
    return form.errors


@bp.post("/delete")
@fresh_login_required
def delete() -> dict:
    """Delete user account."""
    form = DeleteForm()
    if form.validate_on_submit():
        sql("""DELETE FROM contact WHERE email = %s""", (current_user.email,))
        log_account_deletion(current_user.name, current_user.email)
        logout_user()
        flash("Your account has been successfully deleted.")
        return {}
    return form.errors
