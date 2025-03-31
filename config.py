import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://ztn:ztn%40sim@localhost:5432/ztn_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/api/auth/refresh'
    JWT_COOKIE_SECURE = False  # For testing on HTTP
    JWT_COOKIE_CSRF_PROTECT = False  # Disable CSRF protection
    JWT_REFRESH_TOKEN_EXPIRES = 30 * 60  # 30 minutes

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "fallback-in-dev")

    # Flask-Mail Settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')    # The app password you generated
    MAIL_DEFAULT_SENDER = 'bztniplab@gmail.com'  
