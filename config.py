import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # ------------------------
    # 📦 Database Configuration
    # ------------------------
    SQLALCHEMY_DATABASE_URI = "postgresql://ztn:ztn%40sim@localhost:5432/ztn_db"  # For local testing
    # SQLALCHEMY_DATABASE_URI = "postgresql://ztn:ztn%40sim@db:5432/ztn_db"        # For Docker
    # SQLALCHEMY_DATABASE_URI = "postgresql://ztn:ztn%40sim@10.88.0.2:5432/ztn_db" # For Podman
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ------------------------
    # 🔐 JWT & Session Settings
    # ------------------------
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # Token locations and cookies
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token_cookie'
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/api/auth/refresh'  # Scoped to refresh endpoint

    # Expiry durations
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)   # Short-lived for security
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)      # Long-lived to allow auto-refresh

    # Cookie security settings
    JWT_COOKIE_SECURE = False  # Set to True in production (requires HTTPS)
    JWT_COOKIE_SAMESITE = "Lax"  # Lax recommended for login flows
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_CSRF_IN_COOKIES = False

    # # ------------------------
    # # 🔐 Flask Session (WebAuthn or flash messages)
    # # ------------------------
    # SESSION_COOKIE_NAME = "ztn_iam_session"
    # SESSION_COOKIE_DOMAIN = "localhost.localdomain"  # For multi-subdomain testing
    # SESSION_COOKIE_PATH = "/"
    # SESSION_COOKIE_SAMESITE = "Lax"
    # SESSION_COOKIE_SECURE = False  # 🔒 Change to True in production

    # ------------------------
    # ✉️ Mail Configuration
    # ------------------------
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # App password (not your Gmail password)
    MAIL_DEFAULT_SENDER = 'bztniplab@gmail.com'
    ADMIN_ALERT_EMAIL = 'patrick.mutabazi.pj1@g.ext.naist.jp'

    # ------------------------
    # 🔐 Flask App Secret
    # ------------------------
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "fallback-in-dev")
