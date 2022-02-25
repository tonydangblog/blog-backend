"""Test Main Blueprint: Posts."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from flask import url_for
from werkzeug.test import Client

from app.sql import sql


class TestBlog:
    def test_redirects_permanently(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN /blog is requested.
        res = client.get(url_for("main.blog"))
        # THEN Client is redirected permanently.
        assert res.status_code == 301  # nosec

    def test_redirect_blog_to_posts(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN /blog is requested.
        res = client.get(url_for("main.blog"), follow_redirects=True)
        # THEN Client is redirected to posts page.
        assert b"data-posts" in res.data  # nosec


def test_dumps_posts_to_dom(client: Client) -> None:
    # GIVEN Test client and all blog posts.
    posts = sql("""SELECT * FROM page WHERE is_blog_post""", method="all")
    # WHEN Blog archive is requested.
    res = client.get(url_for("main.posts"))
    # THEN All blog posts are present in DOM data.
    for post in posts:
        assert (  # nosec
            post["title"].encode("UTF-8") in res.data,
            post["path"].encode("UTF-8") in res.data,
        ) == (True, True)
