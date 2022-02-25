"""SQL Wrappers.

Psycopg2 wrappers for executing PostgreSQL statements in Flask.
Requires 'DSN' configuration variable to be set in Flask.
"""

from types import TracebackType
from typing import Any, Type, Union

from flask import current_app
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Identifier


class DbCtx:
    """Context manager for database connections.

    Note: psycopg2.connect().rollback() is automatically called if an exception
    is raised within with block.
    """

    def __init__(self, dsn: str = None) -> None:
        """Set DSN if given else default to Flask app 'DSN' configuration variable."""
        self.dsn = dsn or current_app.config["DSN"]

    def __enter__(self):
        """Connect to database and open cursor."""
        self.conn = connect(self.dsn)
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        return self.cur

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        """Commit unsaved changes then close cursor and connection."""
        self.conn.commit()
        self.cur.close()
        self.conn.close()


def sql(
    stmt: str,
    values: Union[tuple, dict[str, Any]] = None,
    method: str = None,
    dsn: str = None,
) -> Any:
    """Execute SQL statement and optionally fetch resulting row(s) or row count.

    :param stmt: SQL statement. (E.g. 'SELECT * FROM table_name')
    :param values: Values in a tuple (to use with placeholders '%s'), OR in a dict
                   (to use with name parameters '%(param)s') in the SQL statement.
    :param method: Fetch method ("one", "all") or "row" for row count.
    :param dsn: Database DSN.
    """
    with DbCtx(dsn) as cur:
        if values:
            cur.execute(stmt, values)
        else:
            cur.execute(stmt)
        if method == "one":
            return cur.fetchone()
        if method == "all":
            return cur.fetchall()
        if method == "count":
            return cur.rowcount
    return None


def fetch_one(table: str, column: str, value: str, dsn: str = None) -> Any:
    """Fetch one row in given table using column and unique value."""
    stmt = SQL("""SELECT * FROM {table} WHERE {column} = %s""").format(
        table=Identifier(table), column=Identifier(column)
    )
    return sql(stmt, (value,), "one", dsn)
