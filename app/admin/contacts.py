"""Admin Blueprint: Contacts."""

from flask import flash, redirect
from werkzeug.wrappers import Response

from app.admin import ListView, bp
from app.forms import UUIDForm
from app.sql import sql


class ContactListView(ListView):
    """Contact table list view."""

    primary_key = "contact_id"
    stmt = """
           SELECT * FROM contact
           JOIN role USING (role_id)
           JOIN mailing_list USING (mailing_list_id)
           """
    filters = [
        ("is subscriber", "WHERE is_subscriber "),
        ("not is subscriber", "WHERE NOT is_subscriber "),
        ("is verified", "WHERE is_verified "),
        ("not is verified", "WHERE NOT is_verified "),
        ("is banned", "WHERE is_banned "),
        ("not is banned", "WHERE NOT is_banned "),
    ]
    hidden_columns = ["role_id", "mailing_list_id", "contact_id", "token"]
    actions = ["ban_contact"]


bp.add_url_rule("/contacts", view_func=ContactListView.as_view("contacts"))


@bp.post("/contacts/ban")
def ban_contact() -> Response:
    """Ban contact."""
    form = UUIDForm()
    if form.validate_on_submit():
        stmt = """
               UPDATE contact
               SET is_verified = false, is_subscriber = false, is_banned = true
               WHERE contact_id = %s
               """
        sql(stmt, (form.uuid.data,))
        flash("Contact banned.")
    form.flash_error()
    return redirect(form.next_url.data)
