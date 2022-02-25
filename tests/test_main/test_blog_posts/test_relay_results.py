"""Test Main Blueprint: Relay Results."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from json import loads

from flask import url_for
from werkzeug.test import Client


class TestRelayResultsView:
    def test_returns_relay_events_for_init_page_load(self, client: Client) -> None:
        # GIVEN Test Client.
        # WHEN Relay results post is requested.
        res = client.get(url_for("main.relay_results"))
        # THEN Event dates and locations are present in page.
        actual = (b"2019-08-04" in res.data, b"Lake Elizabeth" in res.data)
        assert actual == (True, True)  # nosec


class TestRelayResultsResults:
    def test_returns_results_data(self, client: Client) -> None:
        # GIVEN Test Client.
        # WHEN Request is made for results data with valid date.
        res = client.get(url_for("main.relay_results_results", run_date="2021-08-27"))
        # THEN Expect JSON data is returned.
        assert loads(res.data) == {  # nosec
            "keys": ["1", "2", "3", "4"],
            "members_per_team": 4,
            "team_names": ["A", "B"],
            "team_results": [
                {
                    "runners": {"1": "Tony", "2": "Nicole", "3": "Jess", "4": "Jay"},
                    "team": "A",
                    "total_time": 3753.0,
                    "1": 933.0,
                    "2": 964.0,
                    "3": 1120.0,
                    "4": 736.0,
                },
                {
                    "runners": {
                        "1": "Mesh",
                        "2": "Allen",
                        "3": "Connie",
                        "4": "Praneil",
                    },
                    "team": "B",
                    "total_time": 3699.0,
                    "1": 883.0,
                    "2": 990.0,
                    "3": 954.0,
                    "4": 872.0,
                },
            ],
            "xMax": 3753.0,
        }


class TestRelayResultsPaces:
    def test_returns_paces_data(self, client: Client) -> None:
        # GIVEN Test Client.
        # WHEN request is made for paces data with valid date.
        res = client.get(url_for("main.relay_results_paces", run_date="2021-08-27"))
        # THEN Expect JSON data is returned.
        assert loads(res.data) == [  # nosec
            {"name": "Jay", "pace": 368.0},
            {"name": "Praneil", "pace": 436.0},
            {"name": "Mesh", "pace": 441.5},
            {"name": "Tony", "pace": 466.5},
            {"name": "Connie", "pace": 477.0},
            {"name": "Nicole", "pace": 482.0},
            {"name": "Allen", "pace": 495.0},
            {"name": "Jess", "pace": 560.0},
        ]


class TestRelayResultsTrends:
    def test_returns_trends_data(self, client: Client) -> None:
        # GIVEN Test Client.
        # WHEN request is made for trends data with valid date.
        res = client.get(url_for("main.relay_results_trends", run_date="2020-08-14"))
        # THEN Expect JSON data is returned.
        assert loads(res.data) == [  # nosec
            [
                {"date": "2019-08-04T00:00:00-08:00", "name": "Tony", "pace": 505.5},
                {"date": "2020-08-14T00:00:00-08:00", "name": "Tony", "pace": 521.0},
            ],
            [
                {"date": "2019-08-04T00:00:00-08:00", "name": "Allen", "pace": 471.5},
                {"date": "2020-08-14T00:00:00-08:00", "name": "Allen", "pace": 493.5},
            ],
            [
                {"date": "2019-08-04T00:00:00-08:00", "name": "Nicole", "pace": 497.5},
                {"date": "2020-08-14T00:00:00-08:00", "name": "Nicole", "pace": 486.5},
            ],
            [
                {"date": "2019-08-04T00:00:00-08:00", "name": "Jay", "pace": 402.0},
                {"date": "2020-08-14T00:00:00-08:00", "name": "Jay", "pace": 387.0},
            ],
        ]


class TestRelayResultsNotes:
    def test_returns_notes_data(self, client: Client) -> None:
        # GIVEN Test Client.
        # WHEN request is made for notes data with valid date.
        res = client.get(url_for("main.relay_results_notes", run_date="2019-08-11"))
        # THEN Expect JSON data is returned.
        assert loads(res.data) == [  # nosec
            "Tony/Allen's laps were not timed individually so time shown is average "
            "pace of 2 mile run.",
            "Due to injury during Mesh's second lap, Allen & Nicole subbed in to "
            "complete the lap.",
        ]
