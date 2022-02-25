"""JWT Wrappers.

PyJWT Wrappers for encoding and decoding JWTs in Flask.
Requires 'SECRET_KEY' configuration variable to be set in Flask.
"""

from time import time
from typing import Any, Optional

from flask import current_app
from jwt import decode, encode
from jwt.exceptions import InvalidTokenError


def generate_jwt(expires_in: Optional[int] = 600, **payload: Any) -> str:
    """Generate JWT.

    :param expires_in: Time until expiration in seconds (default 10 minutes). Allows no
                       expiration if None is passed as argument.
    :param payload: JWT payload as optional keyword arguments.
    """
    payload["iat"] = time()
    if expires_in:
        payload["exp"] = time() + expires_in
    return encode(payload, current_app.config["SECRET_KEY"])


def decode_jwt(jwt: str) -> Optional[dict[str, Any]]:
    """Decode JWT. If valid JWT, return payload as dictionary, else return None."""
    try:
        payload = decode(jwt, current_app.config["SECRET_KEY"], ["HS256"])
    except InvalidTokenError:
        return None
    return payload
