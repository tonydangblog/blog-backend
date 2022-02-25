"""Test SQL Wrappers."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from psycopg2 import InterfaceError
from pytest import mark, raises
from werkzeug.test import Client

from app.sql import DbCtx, fetch_one, sql


class TestDatabaseContextManager:
    cases = [None, "dbname=blog_test"]
    ids = [f"DSN: {case}" for case in cases]

    @mark.parametrize("dsn", cases, ids=ids)
    def test_sets_up_and_tears_down(self, client: Client, dsn: str) -> None:
        # GIVEN Test client for app context and SQL statement.
        stmt = """SELECT * FROM contact WHERE email = 'tony@tonydang.blog'"""
        # WHEN Using database context manager.
        with DbCtx(dsn) as cur:
            cur.execute(stmt)
            contact = cur.fetchone()
        # THEN Confirm database connection is set up and torn down.
        assert contact["preferred_name"] == "Tony"  # nosec
        with raises(InterfaceError):
            cur.execute(stmt)


class TestSQLWrapper:
    def test_executes_insert_with_named_params(self, client: Client) -> None:
        # GIVEN Test client for app context, SQL statement, and named parameters.
        stmt = """
               INSERT INTO contact (name, preferred_name, email, token)
               VALUES (%(name)s, %(preferred_name)s, %(email)s, %(token)s)
               """
        values = {
            "name": "Tony",
            "preferred_name": "Tony",
            "email": "tonytadang@gmail.com",
            "token": "test",
        }
        # WHEN INSERT statement is executed with named parameters.
        sql(stmt, values)
        # THEN INSERT statement succeeds.
        assert fetch_one("contact", "token", "test")  # nosec

    def test_executes_update_with_positional_params_select_and_fetch_one(
        self, client: Client
    ) -> None:
        # GIVEN Test client for app context.
        # WHEN UPDATE & SELECT statements are executed with positional parameters then
        #      fetched.
        sql("""UPDATE contact set name = 'Kari' WHERE token = %s""", ("unv1",))
        contact = sql("""SELECT * FROM contact WHERE token = %s""", ("unv1",), "one")
        # THEN UPDATE & SELECT statements and fetch succeeds.
        assert contact["name"] == "Kari"  # nosec

    def test_executes_delete_and_fetch_all(self, client: Client) -> None:
        # GIVEN Test client for app context.
        # WHEN DELETE and fetch all statements are executed.
        sql("""DELETE FROM contact WHERE token = 'unv1'""")
        contacts = sql("""SELECT * FROM contact""", method="all")
        # THEN DELETE and fetch all statements succeeds.
        assert len(contacts) == 5  # nosec

    def test_executes_row_count(self, client: Client) -> None:
        # GIVEN Test client for app context.
        # WHEN Row count statement is executed.
        # THEN Row count is returned.
        assert sql("""SELECT * FROM contact""", method="count") == 6  # nosec


def test_fetch_one(client: Client) -> None:
    # GIVEN Test client for app context.
    # WHEN Row is fetched.
    contact = fetch_one("contact", "email", "tony@tonydang.blog")
    # THEN Dict for row is returned.
    assert contact["preferred_name"] == "Tony"  # nosec
