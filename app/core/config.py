# app/core/config.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from typing import Optional

# Explicitly load the .env file early (adjust path if needed)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

    DATABASE_URL: str = os.getenv("DATABASE_URL")

    AFRICASTALKING_USERNAME: str = os.getenv("AFRICASTALKING_USERNAME")
    AFRICASTALKING_API_KEY: str = os.getenv("AFRICASTALKING_API_KEY")
    AFRICASTALKING_SENDER_ID: str = os.getenv("AFRICASTALKING_SENDER_ID")
    AFRICASTALKING_COUNTRY_CODE: str = os.getenv("AFRICASTALKING_COUNTRY_CODE")
    AFRICASTALKING_SHORTCODE: str = os.getenv("AFRICASTALKING_SHORTCODE")
    AFRICASTALKING_SHORTCODE_TYPE: str = os.getenv("AFRICASTALKING_SHORTCODE_TYPE")
    AFRICASTALKING_SHORTCODE_SERVICE: str = os.getenv("AFRICASTALKING_SHORTCODE_SERVICE")
    MYSQL_USERNAME: Optional[str] = os.getenv("MYSQL_USERNAME")
    MYSQL_PASSWORD: Optional[str] = os.getenv("MYSQL_PASSWORD")

    class Config:
        env_file = env_path

settings = Settings()

print("Database URL in config:", settings.DATABASE_URL)
