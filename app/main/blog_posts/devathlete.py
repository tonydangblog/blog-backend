"""Main Blueprint: devathlete."""

from app.main import BlogPostView, bp

bp.add_url_rule("/devathlete", view_func=BlogPostView.as_view("devathlete"))
