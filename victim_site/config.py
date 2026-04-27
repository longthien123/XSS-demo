import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_PATH = BASE_DIR / "database.db"
COOKIES_LOG_PATH = BASE_DIR / "cookies.txt"
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

USE_MYSQL = DATABASE_URL.startswith("mysql://") or DATABASE_URL.startswith("mysql+pymysql://")
SECRET_KEY = os.getenv("SECRET_KEY", "xss-demo-secret-key-change-me")


def get_secure_mode(argv):
    return "--secure" in argv
