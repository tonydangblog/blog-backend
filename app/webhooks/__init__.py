"""Initialize Webhooks Blueprint."""

from flask import Blueprint

bp = Blueprint("webhooks", __name__, url_prefix="/webhooks")

from app.webhooks import stripe
