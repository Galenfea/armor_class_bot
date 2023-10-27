import logging
import os
from typing import Optional

from aiogram import Bot
from dotenv import load_dotenv

from exceptions import EnvError

logger = logging.getLogger(__name__)


class SingletonBot:
    instance: Optional[Bot] = None

    @staticmethod
    def check_token(bot_token: str) -> None:
        if not bot_token:
            logger.critical("Environment variable error")
            raise EnvError("Environment variable error")

    def __new__(cls):
        if cls.instance is None:
            load_dotenv()
            BOT_TOKEN = os.getenv("BOT_TOKEN")
            cls.check_token(BOT_TOKEN)
            cls.instance = Bot(token=BOT_TOKEN)
        return cls.instance

    def __getattr__(self, name: str):
        if self.instance is not None:
            return getattr(self.instance, name)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )
