import logging
import os
from logging.config import dictConfig
from typing import Optional

from aiogram import Bot
from dotenv import load_dotenv

from exceptions import EnvError
from log_config import log_config

dictConfig(log_config)
logger = logging.getLogger(__name__)


class SingletonBot:
    instance: Optional[Bot] = None

    @staticmethod
    def check_token(bot_token: str) -> None:
        if not bot_token:
            logger.critical("Environment variable error")
            raise EnvError("Environment variable error")

    def __new__(cls):
        logger.debug("__new__ SingletonBot")
        logger.debug(f"Bot instance = {cls.instance}")
        if cls.instance is None:
            load_dotenv()
            BOT_TOKEN = os.getenv("BOT_TOKEN")
            logger.debug("Bot token: %s", BOT_TOKEN)
            cls.check_token(BOT_TOKEN)
            cls.instance = Bot(token=BOT_TOKEN)
        return cls.instance

    def __getattr__(self, name: str):
        if self.instance is not None:
            return getattr(self.instance, name)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )
