"""Test Admin Blueprint: Relay Runs."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from flask import url_for
from pytest import mark
from werkzeug.test import Client

from app.admin.relay_runs import RelayRunForm
from app.sql import fetch_one, sql
from tests.markers import skipif_sends_email


class TestRelayRunForm:
    cases = [
        ("Valid run", "name", "Tony", True),
        ("Empty date", "run_date", "", False),
        ("Invalid date", "run_date", "2021-08-0", False),
        ("Invalid location id", "relay_run_location_id", "0", False),
        ("Invalid leg_distance", "leg_distance", "0", False),
        ("Min leg_distance", "leg_distance", "0.01", True),
        ("Max leg_distance", "leg_distance", "999.99", True),
        ("Invalid team name", "team", "AA", False),
        ("Invalid position", "position", "0", False),
        ("Invalid time format", "time", "10:00", False),
        ("Time with precision", "time", "127:10:00.123456", True),
    ]
    ids = [case[0] for case in cases]

    @mark.parametrize("case_id, key, value, expected", cases, ids=ids)
    def test_validates(
        self,
        client: Client,
        case_id: str,
        key: str,
        value: str,
        expected: bool,
    ) -> None:
        # GIVEN Test client, POST data, and expected validation result.
        # WHEN Form instance is instantiated with POST data.
        data = {
            "run_date": "2021-08-08",
            "relay_run_location_id": "1",
            "leg_distance": "2.00",
            "team": "A",
            "position": "1",
            "name": "Tony",
            "time": "00:10:00",
            "notes": "",
        }
        data[key] = value
        client.post(url_for("main.home"), data=data)
        locations = sql("""SELECT * FROM relay_run_location""", method="all")
        location_choices = [location["relay_run_location_id"] for location in locations]
        form = RelayRunForm()
        form.relay_run_location_id.choices = location_choices
        # THEN Form validates as expected.
        assert form.validate_on_submit() == expected  # nosec


class TestRelayRunListView:
    @skipif_sends_email
    def test_shows_relay_runs(self, client: Client, authenticated_admin: None) -> None:
        # GIVEN Test client with authenticated admin.
        # WHEN Admin relay runs page is requested.
        res = client.get(url_for("admin.relay_runs"))
        # THEN Admin relay runs page is shown.
        assert b"SELECT * FROM relay_run" in res.data  # nosec


class TestInsertRelayRun:
    @skipif_sends_email
    def test_inserts_relay_run(self, client: Client, authenticated_admin: None) -> None:
        # GIVEN Test client with authenticated admin.
        # WHEN POST request is made to insert a relay run.
        data = {
            "next_url": "/admin/relay-runs",
            "run_date": "2099-09-09",
            "relay_run_location_id": "1",
            "leg_distance": "2.00",
            "team": "A",
            "position": "1",
            "name": "Tony",
            "time": "00:10:00",
            "notes": "",
        }
        res = client.post(
            url_for("admin.insert_relay_run"), data=data, follow_redirects=True
        )
        # THEN Run is added, success message is flashed, and redirected to admin.
        assert fetch_one("relay_run", "run_date", "2099-09-09")  # nosec
        actual = (b"Run added." in res.data, b"Relay Runs | Tony Dang" in res.data)
        assert actual == (True, True)  # nosec

    @skipif_sends_email
    def test_shows_form_errors(self, client: Client, authenticated_admin: None) -> None:
        # GIVEN Test client with authenticated admin.
        # WHEN POST Request is made to insert relay run with invalid POST data.
        data = {
            "next_url": "/admin/relay-runs",
            "run_date": "2099-09-0",
            "name": "Tony",
        }
        res = client.post(
            url_for("admin.insert_relay_run"), data=data, follow_redirects=True
        )
        # THEN Error message is flashed.
        assert b"Not a valid date value" in res.data  # nosec


class TestDeleteRelayRun:
    @skipif_sends_email
    def test_deletes_relay_run(self, client: Client, authenticated_admin: None) -> None:
        # GIVEN Test client with authenticated admin.
        # WHEN POST request is made to delete relay run.
        relay_run = sql("""SELECT * FROM relay_run""", method="one")
        data = {"next_url": "/admin/relay-runs", "uuid": relay_run["relay_run_id"]}
        res = client.post(
            url_for("admin.delete_relay_run"), data=data, follow_redirects=True
        )
        # THEN Run is deleted, success message is flashed, and redirected to admin.
        relay_run = fetch_one("relay_run", "relay_run_id", relay_run["relay_run_id"])
        assert not relay_run  # nosec
        actual = (b"Run deleted." in res.data, b"Relay Runs | Tony Dang" in res.data)
        assert actual == (True, True)  # nosec

    @skipif_sends_email
    def test_shows_form_errors(self, client: Client, authenticated_admin: None) -> None:
        # GIVEN Test client with authenticated admin.
        # WHEN POST Request is made to delete relay run with invalid POST data.
        data = {"next_url": "/admin/relay-runs", "uuid": ""}
        res = client.post(
            url_for("admin.delete_relay_run"), data=data, follow_redirects=True
        )
        # THEN Error message is flashed.
        assert b"Invalid UUID." in res.data  # nosec
