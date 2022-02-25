"""Main Blueprint: Posts."""

from json import dumps

from flask import redirect, url_for
from werkzeug.wrappers import Response

from app.main import bp
from app.render import render_html
from app.sql import sql


@bp.get("/blog")
def blog() -> Response:
    """Redirect /blog -> /posts."""
    return redirect(url_for("main.posts"), code=301)


@bp.get("/posts")
def posts() -> str:
    """Display blog posts."""
    blog_posts = sql(
        """SELECT title, path FROM page WHERE is_blog_post ORDER BY post_date DESC""",
        method="all",
    )
    return render_html("main/main/posts/posts.html", blog_posts=dumps(blog_posts))
