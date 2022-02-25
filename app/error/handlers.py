"""Error Blueprint: Handlers."""

from typing import Union

from flask import flash, request
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import InternalServerError, NotFound
from werkzeug.http import HTTP_STATUS_CODES

from app.error import bp
from app.error.emails import send_error_email
from app.error.loggers import csrf_logger
from app.render import render_html
from app.sql import fetch_one

ErrorResponse = tuple[Union[str, dict], int]


def prefers_json() -> bool:
    """Check if JSON is preferred response type."""
    return (
        request.accept_mimetypes["application/json"]
        >= request.accept_mimetypes["text/html"]
    )


def json_error_response(status_code: int, message: str = None) -> tuple[dict, int]:
    """Return JSON error response."""
    payload = {"error": HTTP_STATUS_CODES.get(status_code, "Unknown Error")}
    if message:
        payload["message"] = message
    return payload, status_code


def error_response(error_code: int, message: str) -> ErrorResponse:
    """Return error response."""
    if prefers_json():
        flash(message)
        return json_error_response(error_code, message)
    page = fetch_one("page", "path", "/error/whoops")
    return (
        render_html("error/whoops/whoops.html", whoops_message=message, page=page),
        error_code,
    )


@bp.app_errorhandler(404)
def handle_not_found_error(err: NotFound) -> ErrorResponse:
    """Handle 404 Error."""
    return error_response(err.code, "404 - Whoops, resource not found...")


@bp.app_errorhandler(500)
def handle_internal_server_error(err: InternalServerError) -> ErrorResponse:
    """Handle 500 Error."""
    send_error_email(err)
    return error_response(err.code, "500 - Whoops, something went wrong...")


@bp.app_errorhandler(CSRFError)
def handle_csrf_error(err: CSRFError) -> ErrorResponse:
    """Handle CSRF Error."""
    csrf_logger.info("%s - %s\n%s", err.code, err.name, err.description)
    return error_response(err.code, "400 - Invalid CSRF token.")
