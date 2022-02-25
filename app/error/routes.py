"""Error Blueprint: Routes."""

from flask import abort, current_app

from app.error import bp


@bp.get("/500")
def internal_server_error() -> str:
    """Show internal server error page for testing."""
    if current_app.testing:
        abort(500)
    abort(404)
