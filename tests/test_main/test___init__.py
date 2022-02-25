"""Test Main Blueprint: Initialization."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from re import match

from flask import url_for
from pytest import mark
from werkzeug.test import Client

from app.date import format_date
from app.sql import fetch_one, sql


class TestBlogPostView:
    def test_renders_blog_post_date(self, client: Client) -> None:
        # GIVEN Test client.
        # WHEN Blog post is requested.
        page = sql("""SELECT * FROM page WHERE is_blog_post""", method="one")
        res = client.get(page["path"])
        # THEN Post date is displayed on rendered page.
        date = format_date(page["post_date"], "%B {do}, %Y")
        assert date.encode("UTF-8") in res.data  # nosec

    def test_renders_prev_post_button(self, client: Client) -> None:
        # GIVEN Test Client.
        # WHEN Blog post with a previous post is requested.
        stmt = """SELECT * FROM page WHERE is_blog_post ORDER BY post_date DESC"""
        page = sql(stmt, method="one")
        res = client.get(page["path"])
        # THEN Previous post button is displayed on page.
        assert b"<button>PREVIOUS</button>" in res.data  # nosec
        assert b"<button>NEXT</button>" not in res.data  # nosec

    def test_renders_next_post_button(self, client: Client) -> None:
        # GIVEN Test Client.
        # WHEN Blog post with a next post is requested.
        stmt = """SELECT * FROM page WHERE is_blog_post ORDER BY post_date"""
        page = sql(stmt, method="one")
        res = client.get(page["path"])
        # THEN NEXT post button is displayed on page.
        assert b"<button>PREVIOUS</button>" not in res.data  # nosec
        assert b"<button>NEXT</button>" in res.data  # nosec


class TestStaticFromRoot:
    cases = ["favicon.ico", "robots.txt"]

    @mark.parametrize("file", cases)
    def test_returns_static_files_from_root(self, client: Client, file: str) -> None:
        # GIVEN Test client.
        # WHEN Static file is requested from root.
        res = client.get(f"/{file}")
        # THEN Static file is present.
        assert res.status_code == 200  # nosec


class TestPageProperties:
    cases = [
        "a_nomadic_experiment",
        "bee_snapped",
        "devathlete",
        "relay_results",
        "subielife",
        "about",
        "contact",
        "home",
        "now",
        "posts",
        "support",
    ]

    @mark.parametrize("endpoint", cases)
    def test_exists_in_database(self, client: Client, endpoint: str) -> None:
        # GIVEN Test client for application context.
        # WHEN Page is fetched from database.
        # THEN Page exists.
        assert fetch_one("page", "path", url_for(f"main.{endpoint}"))  # nosec


def test_displays_main_blueprint_pages(client: Client) -> None:
    # GIVEN Test client and all main blueprint pages.
    all_pages = sql("""SELECT * FROM page""", method="all")
    main_bp_pages = [
        page
        for page in all_pages
        if not match(r"/.+/", page["path"])
        and page["path"] not in ("/admin", "/mailer", "/sandbox")
    ]
    # WHEN Page is requested.
    # THEN Page is rendered.
    for page in main_bp_pages:
        res = client.get(page["path"])
        assert res.status_code == 200  # nosec
        if page["title"]:
            assert f"{page['title']} | Tony Dang".encode("UTF-8") in res.data  # nosec
