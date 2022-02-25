"""Test Fixtures."""

from pathlib import Path
from typing import Generator

from flask import Flask, url_for
from pytest import fixture
from werkzeug.test import Client

from app import create_app
from app.jwt import generate_jwt
from app.sql import sql
from config import DevConfig, TestConfig


@fixture
def app() -> Generator[Flask, None, None]:
    # SETUP Flask app with testing configuration and reset test database.
    app = create_app(TestConfig)
    stmt = Path(__file__).parents[2] / "database" / "dist" / "test.sql"
    with app.app_context():
        sql(stmt.read_text())
    # TEST
    yield app
    # TEARDOWN N/A.


@fixture
def client(app: Flask) -> Generator[Client, None, None]:
    # SETUP Test client with application context and make initial GET request to app.
    with app.test_client() as client:
        with app.app_context():
            client.get("/")
            # TEST
            yield client
    # TEARDOWN With block ends.


@fixture
def dev_client() -> Generator[Client, None, None]:
    # SETUP Test client with development configuration and make initial GET request.
    app = create_app(DevConfig)
    with app.test_client() as dev_client:
        dev_client.get("/")
        # TEST
        yield dev_client
    # TEARDOWN With block ends.


@fixture
def clear_logs() -> Generator[None, None, None]:
    # SETUP Clear logs.
    log_directories = sorted((Path(__file__).parents[1] / "logs").glob("*"))
    log_files = [
        sorted(directory.glob("*"))[0]
        for directory in log_directories
        if directory.is_dir()
    ]
    for log in log_files:
        log.write_text("")
    # TEST
    yield
    # TEARDOWN Clear logs.
    for log in log_files:
        log.write_text("")


@fixture
def authenticated_admin(client: Client) -> None:
    # SETUP Authenticate an admin login.
    jwt = generate_jwt(token="adm1", bp="auth")
    client.get(url_for("auth.authenticate", jwt=jwt))
    # TEST
    # TEARDOWN N/A.


@fixture
def authenticated_user(client: Client) -> None:
    # SETUP Authenticate a user login.
    jwt = generate_jwt(token="sub1", bp="auth")
    client.get(url_for("auth.authenticate", jwt=jwt))
    # TEST
    # TEARDOWN N/A.
