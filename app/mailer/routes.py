"""Mailer Blueprint: Routes."""

from typing import Union

from flask import abort, flash, redirect, url_for
from flask_login import current_user
from werkzeug.wrappers import Response

from app.mailer import bp
from app.mailer.emails import send_list_email
from app.mailer.forms import MailForm
from app.mailer.loggers import log_list_mail
from app.render import render_html
from app.sql import sql


@bp.before_request
def admin_only() -> None:
    """Restrict entire blueprint to admin users only."""
    if not current_user.is_authenticated or current_user.role_id != 2:
        abort(404)


@bp.route("", methods=("GET", "POST"))
def index() -> Union[str, Response]:
    """Display mailer index page."""
    mailing_lists = sql("""SELECT * FROM mailing_list""", method="all")
    form = MailForm()
    form.mailing_list_id.choices = [
        mailing_list["mailing_list_id"] for mailing_list in mailing_lists
    ]
    if form.validate_on_submit():
        stmt = """SELECT * FROM contact WHERE is_subscriber AND mailing_list_id = %s"""
        contacts = sql(stmt, (form.mailing_list_id.data,), "all")
        count = sql(stmt, (form.mailing_list_id.data,), "count")
        for contact in contacts:
            send_list_email(
                contact["preferred_name"], contact["email"], contact["token"]
            )
            log_list_mail(contact["name"], contact["email"])
        flash(f"Sending to {count} recipients... See logs.")
        return redirect(url_for("mailer.index"))
    form.flash_error()
    return render_html("mailer/index/index.html", mailing_lists=mailing_lists)
