"""Render Module.

Helper functions for rendering HTML templates.
"""

from os.path import getmtime
from typing import Any, Optional

from flask import render_template, request
from flask_login import current_user

from app.sql import fetch_one


def static_file(path: str) -> str:
    """Generate static file path with version."""
    version = getmtime(f"app/static/{path}")
    return f"/static/{path}?v={version}"


def render_html(template: str, **kwargs: Any) -> str:
    """Render template wrapper for HTML pages."""
    # Use passed page properties if given, else use requested path page properties.
    if kwargs.get("page"):
        page = kwargs["page"]
        kwargs.pop("page")
    else:
        page = fetch_one("page", "path", request.path)

    # Determine navigation endpoints to display.
    if page["is_admin_page"]:
        navigation_endpoints = [
            ("admin.contacts", "contacts"),
            ("admin.pages", "pages"),
            ("admin.relay_runs", "relay runs"),
        ]
    else:
        navigation_endpoints = [
            ("main.posts", "posts"),
            ("main.about", "about"),
            ("main.now", "now"),
            ("main.contact", "contact"),
            ("main.support", "☕ buy me a coffee?"),
        ]

    # Show links to account settings and logout endpoint if user is authenticated.
    if current_user.is_authenticated:
        authenticated_endpoints: Optional[list[tuple[str, str]]] = [
            ("account.settings", current_user.email),
            ("auth.logout", "logout"),
        ]
    else:
        authenticated_endpoints = None

    return render_template(
        template,
        page=page,
        getmtime=getmtime,
        static_file=static_file,
        title=f"{page['title']} | Tony Dang" if page["title"] else "Tony Dang",
        navigation_endpoints=navigation_endpoints,
        authenticated_endpoints=authenticated_endpoints,
        main_class="main--narrow" if page["is_narrow"] else "",
        site_footer_modifier="site-footer--narrow" if page["is_narrow"] else "",
        **kwargs,
    )
