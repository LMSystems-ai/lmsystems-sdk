import os
from typing import Optional

class Config:
    DEFAULT_BASE_URL = os.getenv("LMSYSTEMS_BASE_URL", "https://api.lmsystems.ai")

    @staticmethod
    def get_base_url() -> str:
        return os.environ.get("LMSYSTEMS_BASE_URL", Config.DEFAULT_BASE_URL)