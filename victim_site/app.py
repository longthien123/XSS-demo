import os
import sys
from datetime import datetime
from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from config import COOKIES_LOG_PATH, SECRET_KEY, USE_MYSQL, get_secure_mode
from db import db_execute, get_db_connection, init_db
from security import admin_required, login_required, validate_comment_input

# Chay secure mode bang: python app.py --secure
SECURE_MODE = get_secure_mode(sys.argv)

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_COOKIE_HTTPONLY"] = True if SECURE_MODE else False


# -------------------------
# Request lifecycle
# -------------------------
@app.before_request
def load_current_user():
    """Nap thong tin user tu session de dung trong route/template."""
    g.user = {
        "id": session.get("user_id"),
        "username": session.get("username"),
        "role": session.get("role"),
    }


@app.after_request
def add_security_headers(response):
    """Them CSP va cac header co ban o secure mode."""
    if SECURE_MODE:
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' https://cdn.jsdelivr.net; script-src 'self' https://cdn.jsdelivr.net"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
    return response


@app.context_processor
def inject_globals():
    return {"secure_mode": SECURE_MODE, "app_mode": "SECURE" if SECURE_MODE else "VULNERABLE"}


# -------------------------
# Routes
# -------------------------
@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    db_execute(
        cur,
        """
        SELECT comments.id, comments.content, comments.created_at, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        ORDER BY comments.id DESC
        LIMIT 6
        """,
    )
    recent_comments = cur.fetchall()
    conn.close()

    return render_template("index.html", recent_comments=recent_comments)


@app.route("/products")
def products():
    return render_template("products.html")


@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    if request.method == "POST":
        comment = request.form.get("comment", "")

        if SECURE_MODE:
            valid, message = validate_comment_input(comment)
            if not valid:
                flash(message, "danger")
                return redirect(url_for("contact"))

        conn = get_db_connection()
        cur = conn.cursor()
        created_at_value = datetime.now() if USE_MYSQL else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db_execute(
            cur,
            "INSERT INTO comments (user_id, content, created_at) VALUES (?, ?, ?)",
            (g.user["id"], comment, created_at_value),
        )
        conn.commit()
        conn.close()

        flash("Gui lien he thanh cong.", "success")
        return redirect(url_for("contact"))

    conn = get_db_connection()
    cur = conn.cursor()
    db_execute(
        cur,
        """
        SELECT comments.id, comments.content, comments.created_at, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        ORDER BY comments.id DESC
        """,
    )
    comments = cur.fetchall()
    conn.close()

    return render_template("contact.html", comments=comments)


@app.route("/user")
@login_required
def user_page():
    return redirect(url_for("contact"))


@app.route("/dashboard")
@admin_required
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    db_execute(cur, "SELECT COUNT(*) AS total_users FROM users")
    total_users = cur.fetchone()["total_users"]
    db_execute(cur, "SELECT COUNT(*) AS total_comments FROM comments")
    total_comments = cur.fetchone()["total_comments"]
    conn.close()

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_comments=total_comments,
    )


@app.route("/admin")
@admin_required
def admin():
    return redirect(url_for("dashboard"))


@app.route("/admin/users")
@admin_required
def admin_users():
    conn = get_db_connection()
    cur = conn.cursor()
    db_execute(
        cur,
        """
        SELECT id, username, role
        FROM users
        ORDER BY id ASC
        """,
    )
    users = cur.fetchall()
    conn.close()

    return render_template("admin_users.html", users=users)


@app.route("/admin/comments")
@admin_required
def admin_comments():
    conn = get_db_connection()
    cur = conn.cursor()
    db_execute(
        cur,
        """
        SELECT comments.id, comments.content, comments.created_at, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        ORDER BY comments.id DESC
        """,
    )
    comments = cur.fetchall()
    conn.close()

    return render_template("admin_comments.html", comments=comments)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Vui long nhap day du username va password.", "danger")
            return render_template("register.html")

        conn = get_db_connection()
        cur = conn.cursor()
        db_execute(cur, "SELECT id FROM users WHERE username = ?", (username,))
        existed = cur.fetchone()
        if existed:
            conn.close()
            flash("Username da ton tai.", "danger")
            return render_template("register.html")

        db_execute(
            cur,
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), "user"),
        )
        conn.commit()
        conn.close()

        flash("Dang ky thanh cong. Hay dang nhap.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db_connection()
        cur = conn.cursor()
        db_execute(cur, "SELECT id, username, password, role FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash("Dang nhap thanh cong.", "success")

            if user["role"] == "admin":
                return redirect(url_for("dashboard"))
            return redirect(url_for("index"))

        flash("Sai username hoac password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Da dang xuat.", "info")
    return redirect(url_for("index"))


@app.route("/admin/delete/<int:comment_id>", methods=["POST"])
@admin_required
def delete_comment(comment_id):
    conn = get_db_connection()
    cur = conn.cursor()
    db_execute(cur, "DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()

    flash(f"Da xoa comment #{comment_id}", "info")
    return redirect(url_for("admin"))


@app.route("/log")
def log_cookie():
    """Endpoint nhan cookie bi danh cap: /log?cookie=..."""
    stolen_cookie = request.args.get("cookie", "")
    attacker_ip = request.remote_addr or "unknown"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"[{timestamp}] IP={attacker_ip} | cookie={stolen_cookie}\n"
    with open(COOKIES_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)

    return {
        "status": "success",
        "message": "Cookie da duoc ghi vao cookies.txt",
        "cookie": stolen_cookie,
    }


@app.route("/about-security")
def about_security():
    return render_template("about_security.html")


if __name__ == "__main__":
    if USE_MYSQL:
        print("[DB] Dang su dung Railway MySQL qua DATABASE_URL")
    else:
        print("[DB] Dang su dung SQLite local (database.db)")

    init_db()

    # Dam bao file cookies.txt ton tai truoc khi demo.
    if not os.path.exists(COOKIES_LOG_PATH):
        with open(COOKIES_LOG_PATH, "w", encoding="utf-8"):
            pass

    app.run(host="127.0.0.1", port=5000, debug=True)
