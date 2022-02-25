"""Initialize Admin Blueprint."""

from flask import Blueprint, abort, request
from flask.views import View
from flask_login import current_user
from psycopg2.sql import SQL, Identifier

from app.render import render_html
from app.sql import sql

bp = Blueprint("admin", __name__, url_prefix="/admin")


class ListView(View):
    """Base admin list view class."""

    primary_key = ""
    stmt = ""
    filters: list[tuple[str, str]] = []
    hidden_columns: list[str] = []
    actions: list[str] = []

    @staticmethod
    def data() -> dict:
        """Return a data dictionary if needed for page render.

        This method is meant to be overridden in child classes.
        """
        return {}

    def dispatch_request(self) -> str:
        """Render view."""
        filtered = request.args.get("filtered")
        order_by = request.args.get("order_by")
        if filtered:
            self.stmt = self.stmt + self.filters[int(filtered)][1]
        if order_by:
            self.stmt = SQL(self.stmt + """ORDER BY {order_by}""").format(
                order_by=Identifier(order_by)
            )
        rows = sql(self.stmt, method="all")
        return render_html(
            f"{request.path[1:]}{request.path[6:]}.html",
            primary_key=self.primary_key,
            stmt=self.stmt,
            rows=rows,
            count=sql(self.stmt, method="count"),
            filters=self.filters,
            columns=[column for column in rows[0] if column not in self.hidden_columns],
            actions=self.actions,
            data=self.data(),
        )


@bp.before_request
def admin_only() -> None:
    """Restrict entire blueprint to admin users only."""
    if not current_user.is_authenticated or current_user.role_id != 2:
        abort(404)


@bp.get("")
def index() -> str:
    """Display admin index page."""
    return render_html("admin/index/index.html")


from app.admin import contacts, pages, relay_runs
