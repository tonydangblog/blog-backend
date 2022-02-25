"""Main Blueprint: Subielife."""

from app.main import BlogPostView, bp

bp.add_url_rule("/subielife", view_func=BlogPostView.as_view("subielife"))
