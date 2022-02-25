"""Main Blueprint: Initialization."""

from flask import Blueprint, current_app, request, send_from_directory
from flask.views import View
from werkzeug.wrappers import Response

from app.date import format_date
from app.render import render_html
from app.sql import fetch_one, sql

bp = Blueprint("main", __name__)


class StaticPageView(View):
    """Base static page view class."""

    def dispatch_request(self) -> str:
        """Display requested static page."""
        return render_html(f"main/main{request.path}{request.path}.html")


class BlogPostView(View):
    """Base blog post view class."""

    @staticmethod
    def data() -> dict:
        """Return a data dictionary if needed for page render.

        This method is meant to be overridden in child classes.
        """
        return {}

    def dispatch_request(self) -> str:
        """Render blog post view."""
        page = fetch_one("page", "path", request.path)

        stmt = """
               SELECT path FROM page
               WHERE is_blog_post AND post_date < %s
               ORDER BY post_date DESC
               """
        prev_post = sql(stmt, (page["post_date"],), "one")

        stmt = """
               SELECT path FROM page
               WHERE is_blog_post AND post_date > %s
               ORDER BY post_date ASC
               """
        next_post = sql(stmt, (page["post_date"],), "one")

        return render_html(
            f"main/blog-posts{request.path}{request.path}.html",
            post_date=format_date(page["post_date"], "%B {do}, %Y"),
            prev_post=prev_post,
            next_post=next_post,
            data=self.data(),
        )


@bp.get("/favicon.ico")
@bp.get("/robots.txt")
def static_from_root() -> Response:
    """Return static files from root."""
    assert current_app.static_folder is not None  # nosec
    return send_from_directory(current_app.static_folder, request.path[1:])


from app.main.blog_posts import (
    a_nomadic_experiment,
    bee_snapped,
    devathlete,
    relay_results,
    subielife,
)
from app.main.main import about, contact, home, now, posts, support
