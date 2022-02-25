"""Subscription Blueprint: APIs."""

from app.subscription import bp
from app.subscription.forms import SubscriptionForm
from app.subscription.loggers import log_subscription_request


@bp.post("/subscription-form")
def subscription_form() -> dict:
    """Process subscription form request."""
    form = SubscriptionForm()
    if form.validate_on_submit():
        form.process_subscription_request()
        log_subscription_request(form.name.data, form.email.data)
        return {}
    return form.errors
