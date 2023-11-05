import asyncio
import logging
from logging.config import dictConfig

from bot.bot import run_bot
from settings.log_config import log_config

dictConfig(log_config)
logger = logging.getLogger("armor_class_bot")

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.debug("Emergency interruption by keyboard")
        print("Goodbye!")
