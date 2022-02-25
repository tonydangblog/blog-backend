"""Main Blueprint: Bee Snapped."""

from app.main import BlogPostView, bp

bp.add_url_rule("/bee-snapped", view_func=BlogPostView.as_view("bee_snapped"))
