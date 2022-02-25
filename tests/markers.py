"""Test Markers."""

from os import environ

from pytest import mark

skipif_sends_email = mark.skipif(
    environ.get("TEST_EMAIL") == "skip", reason="Prevent excess Amazon SES usage."
)
