import sqlite3
from urllib.parse import unquote, urlparse

import pymysql
from werkzeug.security import generate_password_hash

from config import DATABASE_PATH, DATABASE_URL, USE_MYSQL


def normalize_mysql_url(db_url):
    """Chuyen mysql+pymysql:// ve mysql:// de parse de dang hon."""
    if db_url.startswith("mysql+pymysql://"):
        return db_url.replace("mysql+pymysql://", "mysql://", 1)
    return db_url


def convert_query_placeholders(query):
    """SQLite dung '?', MySQL dung '%s'."""
    if USE_MYSQL:
        return query.replace("?", "%s")
    return query


def db_execute(cursor, query, params=None):
    final_query = convert_query_placeholders(query)
    if params is None:
        cursor.execute(final_query)
    else:
        cursor.execute(final_query, params)


def get_db_connection():
    """Lay ket noi DB: uu tien Railway MySQL neu co DATABASE_URL, nguoc lai dung SQLite."""
    if USE_MYSQL:
        parsed = urlparse(normalize_mysql_url(DATABASE_URL))
        db_name = parsed.path.lstrip("/")

        return pymysql.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=unquote(parsed.username or ""),
            password=unquote(parsed.password or ""),
            database=db_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(admin_password="admin123"):
    """Khoi tao bang users/comments va tao tai khoan admin mac dinh."""
    conn = get_db_connection()
    cur = conn.cursor()

    if USE_MYSQL:
        db_execute(
            cur,
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
        )

        db_execute(
            cur,
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
        )
    else:
        db_execute(
            cur,
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
            """,
        )

        db_execute(
            cur,
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """,
        )

    db_execute(cur, "SELECT id FROM users WHERE username = ?", ("admin",))
    admin = cur.fetchone()
    if not admin:
        db_execute(
            cur,
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", generate_password_hash(admin_password), "admin"),
        )

    conn.commit()
    conn.close()
