"""Test JWT Wrappers."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from time import sleep, time

from pytest import approx, fail
from werkzeug.test import Client

from app.jwt import decode_jwt, generate_jwt


class TestJWTGenerationFunction:
    def test_defaults_to_600_seconds_expiration(self, client: Client) -> None:
        # GIVEN Test client for app context.
        # WHEN JWT is generated without explicit expiration.
        jwt = generate_jwt()
        # THEN Default expiration is 600 seconds.
        payload = decode_jwt(jwt)
        if payload:
            assert payload["exp"] == approx(time() + 600)  # nosec
        else:
            fail()

    def test_allows_no_expiration_if_explicitly_set(self, client: Client) -> None:
        # GIVEN Test client for app context.
        # WHEN JWT is generated with expiration explicitly set to None.
        jwt = generate_jwt(None)
        # THEN 'exp' key is not present in JWT payload.
        payload = decode_jwt(jwt)
        if payload:
            assert "exp" not in payload  # nosec
        else:
            fail()

    def test_sets_non_default_expiration(self, client: Client) -> None:
        # GIVEN Test client for app context.
        # WHEN JWT is generated with explicit expiration.
        jwt = generate_jwt(86400)
        # THEN Given expiration is present in payload.
        payload = decode_jwt(jwt)
        if payload:
            assert payload["exp"] == approx(time() + 86400)  # nosec
        else:
            fail()

    def test_sets_payload(self, client: Client) -> None:
        # GIVEN Test client for app context.
        # WHEN JWT is generated with kwargs.
        jwt = generate_jwt(one=1, two="two")
        # THEN Given kwargs is present in decoded JWT.
        payload = decode_jwt(jwt)
        if payload:
            assert (payload["one"], payload["two"]) == (1, "two")  # nosec
        else:
            fail()


class TestDecodeJWT:
    def test_decodes_jwt(self, client: Client) -> None:
        # GIVEN Test client for application context and a JWT.
        jwt = generate_jwt(data="data")
        # WHEN The JWT is decoded.
        # THEN If valid JWT, returns payload, else returns None.
        payload = decode_jwt(jwt)
        actual = payload["data"] if payload else fail()
        assert (actual, decode_jwt(jwt + "a")) == ("data", None)  # nosec

    def test_expired_jwt(self, client: Client) -> None:
        # GIVEN Test client for application context and an expired JWT.
        jwt = generate_jwt(1)
        sleep(2)
        # WHEN The JWT is decoded.
        # THEN If valid JWT, returns payload, else returns None.
        assert decode_jwt(jwt) is None  # nosec
