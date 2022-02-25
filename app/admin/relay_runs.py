"""Admin Blueprint: Relay Runs."""

from string import ascii_uppercase

from flask import flash, redirect
from werkzeug.wrappers import Response
from wtforms.fields import (
    DateField,
    IntegerField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import NumberRange, Regexp

from app.admin import ListView, bp
from app.forms import NameEmailForm, UUIDForm
from app.forms.filters import filter_all_whitespace, filter_to_float
from app.sql import sql


class RelayRunForm(NameEmailForm):
    """Relay Run Form."""

    email = None
    run_date = DateField()
    relay_run_location_id = SelectField()
    leg_distance = StringField(
        validators=[NumberRange(0.01, 999.99)], filters=[filter_to_float]
    )
    team = SelectField(choices=list(ascii_uppercase))
    position = IntegerField(validators=[NumberRange(1)])
    time = StringField(validators=[Regexp(r"\d*:[0-5][0-9]:[0-5][0-9]\.?\d{0,6}")])
    notes = TextAreaField(filters=[filter_all_whitespace])


class RelayRunListView(ListView):
    """Relay run table list view."""

    primary_key = "relay_run_id"
    stmt = """
           SELECT * FROM relay_run
           JOIN relay_run_location USING (relay_run_location_id)
           """
    filters = [
        ("latest", "WHERE run_date = (SELECT MAX(run_date) FROM relay_run) "),
    ]
    hidden_columns = ["relay_run_id", "relay_run_location_id", "read_only"]
    actions = ["delete_relay_run"]

    @staticmethod
    def data() -> dict:
        """Store relay run locations and ids."""
        locations = sql("""SELECT * FROM relay_run_location""", method="all")
        return {"locations": locations}


bp.add_url_rule("/relay-runs", view_func=RelayRunListView.as_view("relay_runs"))


@bp.post("/relay-runs/insert")
def insert_relay_run() -> Response:
    """Insert a new relay run."""
    locations = sql("""SELECT * FROM relay_run_location""", method="all")
    location_choices = [location["relay_run_location_id"] for location in locations]
    form = RelayRunForm()
    form.relay_run_location_id.choices = location_choices
    if form.validate_on_submit():
        sql(
            """
            INSERT INTO relay_run (
                run_date,
                relay_run_location_id,
                leg_distance,
                team,
                position,
                name,
                time,
                notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                form.run_date.data,
                form.relay_run_location_id.data,
                form.leg_distance.data,
                form.team.data,
                form.position.data,
                form.name.data,
                form.time.data,
                form.notes.data,
            ),
        )
        flash("Run added.")
    form.flash_error()
    return redirect(form.next_url.data)


@bp.post("/relay-runs/delete")
def delete_relay_run() -> Response:
    """Delete a relay run."""
    form = UUIDForm()
    if form.validate_on_submit():
        sql("""DELETE FROM relay_run WHERE relay_run_id = %s""", (form.uuid.data,))
        flash("Run deleted.")
    form.flash_error()
    return redirect(form.next_url.data)
