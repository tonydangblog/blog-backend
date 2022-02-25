"""Account Blueprint: Routes."""

from flask_login import fresh_login_required

from app.account import bp
from app.render import render_html


@bp.get("/settings")
@fresh_login_required
def settings() -> str:
    """Account settings page."""
    return render_html("account/settings/settings.html")
