import re
from functools import wraps

from flask import flash, g, redirect, url_for


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not g.user.get("id"):
            flash("Ban can dang nhap de tiep tuc.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not g.user.get("id"):
            flash("Ban can dang nhap.", "warning")
            return redirect(url_for("login"))
        if g.user.get("role") != "admin":
            flash("Ban khong co quyen vao trang admin.", "danger")
            return redirect(url_for("index"))
        return view_func(*args, **kwargs)

    return wrapped


def validate_comment_input(comment_text):
    """Validate input don gian cho secure mode."""
    if not comment_text or not comment_text.strip():
        return False, "Binh luan khong duoc de trong."

    if len(comment_text) > 500:
        return False, "Binh luan toi da 500 ky tu."

    blocked_pattern = re.compile(r"<\s*script|javascript:|onerror\s*=|onload\s*=", re.IGNORECASE)
    if blocked_pattern.search(comment_text):
        return False, "Noi dung bi chan boi bo loc bao mat (secure mode)."

    return True, "Hop le"
