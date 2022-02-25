"""Main Blueprint: Contact."""

from app.main import StaticPageView, bp

bp.add_url_rule("/contact", view_func=StaticPageView.as_view("contact"))
