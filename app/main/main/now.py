"""Main Blueprint: Now."""

from app.main import StaticPageView, bp

bp.add_url_rule("/now", view_func=StaticPageView.as_view("now"))
