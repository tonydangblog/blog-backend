"""Main Blueprint: Relay Results."""

from json import dumps
from typing import Dict, List, Union

from app.main import BlogPostView, bp
from app.sql import fetch_one, sql


class RelayResultsView(BlogPostView):
    """Relay Results Blog Post."""

    @staticmethod
    def data() -> Dict[str, list]:
        """Return dictionary with list of relay events for initial page load."""
        stmt = """
               SELECT DISTINCT run_date, relay_run_location FROM relay_run
               JOIN relay_run_location USING (relay_run_location_id)
               ORDER BY run_date DESC
               """
        return {"relay_events": sql(stmt, method="all")}


bp.add_url_rule("/relay-results", view_func=RelayResultsView.as_view("relay_results"))


@bp.get("/relay-results/results/<run_date>")
def relay_results_results(run_date: str) -> str:
    """Return relay results data for given run_date."""
    stmt = """SELECT DISTINCT team FROM relay_run WHERE run_date = %s"""
    team_names = [run["team"] for run in sql(stmt, (run_date,), "all")]

    team_results = []
    for team_name in team_names:
        stmt = """SELECT * FROM relay_run WHERE run_date = %s AND team = %s"""
        runs = sql(stmt, (run_date, team_name), method="all")

        team_result = {"runners": {}, "team": team_name, "total_time": 0}
        for run in runs:
            team_result[run["position"]] = run["time"].total_seconds()
            team_result["runners"][run["position"]] = run["name"]
            team_result["total_time"] = (
                team_result["total_time"] + run["time"].total_seconds()
            )

        team_results.append(team_result)

    members_per_team = max(
        [len(team_result["runners"]) for team_result in team_results]
    )

    return dumps(
        {
            "keys": [f"{i + 1}" for i in range(members_per_team)],
            "members_per_team": members_per_team,
            "team_names": sorted(team_names),
            "team_results": sorted(team_results, key=lambda i: i["team"]),
            "xMax": max([team_result["total_time"] for team_result in team_results]),
        }
    )


@bp.get("/relay-results/paces/<run_date>")
def relay_results_paces(run_date: str) -> str:
    """Return all runs with paces for a given date."""
    stmt = """SELECT * FROM relay_run WHERE run_date = %s"""
    runs = sql(stmt, (run_date,), "all")
    data = [
        {
            "name": run["name"],
            "pace": run["time"].total_seconds() / float(run["leg_distance"]),
        }
        for run in runs
    ]

    return dumps(sorted(data, key=lambda i: i["pace"]))


@bp.get("/relay-results/trends/<run_date>")
def relay_results_trends(run_date: str) -> str:
    """Return runner data for all runners on given date."""
    # Get location and all runners that ran on run_date.
    relay_run_location_id = fetch_one("relay_run", "run_date", run_date)[
        "relay_run_location_id"
    ]
    stmt = """SELECT DISTINCT name FROM relay_run WHERE run_date = %s"""
    names = [run["name"] for run in sql(stmt, (run_date,), "all")]

    data = []

    # For each runner...
    for name in names:
        runner: List[Dict[str, Union[str, float]]] = []

        # Get all previous run dates for same relay_run_location_id.
        stmt = """
               SELECT DISTINCT run_date FROM relay_run
               WHERE run_date <= %s::date AND relay_run_location_id = %s AND name = %s
               """
        runs = sql(stmt, (run_date, relay_run_location_id, name), "all")
        dates = [run["run_date"] for run in runs]

        # For each date...
        for date in dates:

            # Get all run times by runner on date.
            stmt = """SELECT * FROM relay_run WHERE run_date = %s AND name = %s"""
            runs = sql(stmt, (date, name), "all")
            times = [run["time"].total_seconds() for run in runs]

            # Append data point to runner's list.
            data_point = {
                "date": date.strftime("%Y-%m-%dT%H:%M:%S-08:00"),
                "name": name,
                "pace": min(times) / float(runs[0]["leg_distance"]),
            }
            runner.append(data_point)

        # Append runner list to data only if runner has ran more than once at location.
        if len(runner) > 1:
            data.append(sorted(runner, key=lambda i: i["date"]))

    return dumps(sorted(data, key=lambda i: i[-1]["pace"], reverse=True))


@bp.get("/relay-results/notes/<run_date>")
def relay_results_notes(run_date: str) -> str:
    """Return all notes for given run date."""
    stmt = """SELECT notes FROM relay_run WHERE run_date = %s ORDER BY position"""
    runs = sql(stmt, (run_date,), "all")
    return dumps([run["notes"] for run in runs if run["notes"]])
