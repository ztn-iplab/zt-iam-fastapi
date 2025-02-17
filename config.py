import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://ztn:ztn%40sim@localhost:5432/ztn_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SECRET_KEY = 'supersecretkey'
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Load from .env
