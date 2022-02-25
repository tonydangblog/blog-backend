"""Main Blueprint: Home."""

from app.main import bp
from app.render import render_html


@bp.get("/")
def home() -> str:
    """Display home page."""
    return render_html("main/main/home/home.html")
