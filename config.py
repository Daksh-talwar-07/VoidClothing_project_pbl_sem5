import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not set. Add a long random value to your .env file.")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024

    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = os.getenv(
        "SESSION_COOKIE_SECURE",
        "False"
    ).lower() == "true"

    DATABASE_URL = os.getenv("DATABASE_URL")

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif DB_HOST:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///void.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = "static/images"