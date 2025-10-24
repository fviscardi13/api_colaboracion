import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "api_secret_key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://api_user:api_password@localhost:5432/colaboracion_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ##SQLALCHEMY_DATABASE_URI = "sqlite:///colaboracion_db.sqlite3"

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_super_secret_key")

    BONITA_BASE_URL = os.getenv("BONITA_BASE_URL", "http://localhost:8080/bonita")
    BONITA_USER = os.getenv("BONITA_USER", "walter.bates")
    BONITA_PASS = os.getenv("BONITA_PASS", "bpm")

    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")