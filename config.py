import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jlpt.db")

APP_ENV = os.getenv("APP_ENV")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8501")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_USE_STARTTLS = os.getenv("SMTP_USE_STARTTLS", "true").lower() == "true"
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USERNAME or "no-reply@example.com")
VERIFICATION_EXPIRY_HOURS = int(os.getenv("VERIFICATION_EXPIRY_HOURS", "24"))
