import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = float(os.getenv("RETRY_DELAY", "2.0"))
    THINKING_LEVEL = os.getenv("THINKING_LEVEL", "enabled")

    @classmethod
    def validate(cls):
        if not cls.API_KEY:
            raise ValueError("DEEPSEEK_API_KEY not set. Create a .env file or set the environment variable.")
