"""Main Blueprint: A Nomadic Experiment."""

from app.main import BlogPostView, bp

bp.add_url_rule(
    "/a-nomadic-experiment", view_func=BlogPostView.as_view("a_nomadic_experiment")
)
