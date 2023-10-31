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
    """
    Implement a singleton pattern for the Bot instance.

    This class ensures that there is only one Bot instance throughout the
    application's lifecycle.
    It also validates the bot token during the initialization.

    Attributes:
        instance (Optional[Bot]): The singleton instance of Bot.
        Initially set to None.
    """

    instance: Optional[Bot] = None

    @staticmethod
    def check_token(bot_token: str) -> None:
        """
        Validate the provided bot token.

        Checks if the bot token is available. If it's not, logs a critical
        error and raises an exception.

        Args:
            bot_token (str): The token to validate.

        Returns:
            None

        Raises:
            EnvError: If the bot token is missing.
        """
        if not bot_token:
            logger.critical("Environment variable error")
            raise EnvError("Environment variable error")

    def __new__(cls):
        """
        Create a new instance or return the existing instance of Bot.

        This method overrides the __new__ method to implement the singleton
        pattern.
        It checks if an instance already exists, and if not, creates one.

        Returns:
            Bot: The singleton instance of Bot.
        """
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
        """
        Get an attribute from the singleton Bot instance.

        Overrides the __getattr__ method to delegate attribute access
        to the Bot instance.

        Args:
            name (str): The name of the attribute to access.

        Returns:
            The attribute from the Bot instance.

        Raises:
            AttributeError: If the Bot instance is None or the attribute
            does not exist.
        """
        if self.instance is not None:
            return getattr(self.instance, name)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )
