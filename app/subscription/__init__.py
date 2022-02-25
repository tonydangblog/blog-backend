"""Initialize Subscription Blueprint."""

from flask import Blueprint

bp = Blueprint("subscription", __name__, url_prefix="/subscription")

from app.subscription import api, routes
