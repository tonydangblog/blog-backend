"""Initialize Account Blueprint."""

from flask import Blueprint

bp = Blueprint("account", __name__, url_prefix="/account")

from app.account import api, routes
