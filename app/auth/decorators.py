"""Auth Blueprint: Decorators."""

from functools import wraps
from typing import Callable, Union

from flask import flash, redirect, request, url_for
from flask_login import current_user
from werkzeug.wrappers import Response

from app import login_manager
from app.error.handlers import json_error_response, prefers_json


@login_manager.unauthorized_handler
def unauthorized() -> Union[Response, tuple[dict, int]]:
    """Handle unauthorized requests for login_required decorator."""
    flash("Please verify your identity to continue.")
    if prefers_json():
        return json_error_response(401)
    return redirect(url_for("auth.login", next_url=request.full_path))


def non_authenticated_user_only(func) -> Callable:
    """Return wrapper to redirect authenticated users from irrelevant routes."""

    @wraps(func)
    def wrapper(*args, **kwargs) -> Union[Callable, Response]:
        if current_user.is_authenticated:
            return redirect(url_for("account.settings"))
        return func(*args, **kwargs)

    return wrapper
