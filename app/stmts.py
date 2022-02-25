"""SQL Statements."""

from app.sql import sql


def insert_contact(name: str, preferred_name: str, email: str, token: str) -> None:
    """Insert new contact into database."""
    stmt = """
           INSERT INTO contact (name, preferred_name, email, token)
           VALUES (%s, %s, %s, %s)
           """
    sql(stmt, (name, preferred_name, email, token))


def update_contact(name: str, preferred_name: str, email: str) -> None:
    """Update name and preferred name for given email."""
    stmt = """UPDATE contact SET name = %s, preferred_name = %s WHERE email = %s"""
    sql(stmt, (name, preferred_name, email))
