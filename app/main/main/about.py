"""Main Blueprint: About."""

from app.main import StaticPageView, bp

bp.add_url_rule("/about", view_func=StaticPageView.as_view("about"))
