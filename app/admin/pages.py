"""Admin Blueprint: Pages."""

from app.admin import ListView, bp


class PageListView(ListView):
    """Page table list view."""

    primary_key = "page_id"
    stmt = """SELECT * FROM page """
    filters = [
        ("is admin page", "WHERE is_admin_page "),
        ("not is admin page", "WHERE NOT is_admin_page "),
        ("is blog post", "WHERE is_blog_post "),
        ("not is blog post", "WHERE NOT is_blog_post "),
    ]
    hidden_columns = ["page_id"]


bp.add_url_rule("/pages", view_func=PageListView.as_view("pages"))
