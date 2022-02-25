"""Initialize Mailer Blueprint."""

from flask import Blueprint

bp = Blueprint("mailer", __name__, url_prefix="/mailer")

from app.mailer import routes
