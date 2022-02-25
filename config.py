"""App Configuration Settings."""
# pylint: disable=too-few-public-methods; Standard Flask pattern for configurations

from os import environ

from boto3 import client
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration settings."""

    SECRET_KEY = environ.get("SECRET_KEY")
    SESSION_PROTECTION = "strong"  # Flask-Login setting
    RECAPTCHA_PUBLIC_KEY = environ.get("RECAPTCHA_PUBLIC_KEY")
    RECAPTCHA_PRIVATE_KEY = environ.get("RECAPTCHA_PRIVATE_KEY")
    ADMINS = ["Tony Dang <tony@tonydang.blog>"]
    SENDER = "Development Server <dev.server.notification@gmail.com>"
    SES = client(
        "ses",
        region_name="us-west-1",
        aws_access_key_id=environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=environ.get("AWS_SECRET_ACCESS_KEY"),
    )
    STRIPE_API_KEY = environ.get("STRIPE_API_KEY_TEST")
    STRIPE_ENDPOINT_SECRET = environ.get("STRIPE_ENDPOINT_SECRET_TEST")
    ONE_TIME_DONATION_PRICE = "price_1JfuaNG5QkTzoEawkKsmmEVI"
    ONE_TIME_DONATION_EXISTING_CONTACT = environ.get(
        "ONE_TIME_DONATION_EXISTING_CONTACT"
    )
    ONE_TIME_DONATION_NON_EXISTING_CONTACT = environ.get(
        "ONE_TIME_DONATION_NON_EXISTING_CONTACT"
    )
    ONE_TIME_DONATION_INVALID_PRODUCT_ID = environ.get(
        "ONE_TIME_DONATION_INVALID_PRODUCT_ID"
    )


class DevConfig(Config):
    """Development configuration settings."""

    DEBUG = True
    DB_NAME = "blog_dev"
    DSN = f"dbname={DB_NAME}"


class ProdConfig(Config):
    """Production configuration settings."""

    SENDER = "Tony Dang <tony@tonydang.blog>"
    DB_NAME = "blog_prod"
    DSN = f"dbname={DB_NAME}"
    STRIPE_API_KEY = environ.get("STRIPE_API_KEY_PROD")
    STRIPE_ENDPOINT_SECRET = environ.get("STRIPE_ENDPOINT_SECRET_PROD")
    ONE_TIME_DONATION_PRICE = "price_1JuOSzG5QkTzoEaw5RoSDqf1"


class TestConfig(Config):
    """Testing configuration settings."""

    TESTING = True
    WTF_CSRF_ENABLED = False
    DB_NAME = "blog_test"
    DSN = f"dbname={DB_NAME}"
