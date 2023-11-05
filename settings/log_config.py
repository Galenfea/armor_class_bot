import os

log_config = {
    "version": 1,
    "handlers": {
        "handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "formatter",
            "filename": os.path.abspath("logs/armor_class_bot.log"),
            "mode": "a",
            "maxBytes": 1000000,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "armor_class_bot": {
            "handlers": ["handler"],
            "level": "INFO",
        },
        "bot": {
            "handlers": ["handler"],
            "level": "INFO",
        },
        "exception_routes": {
            "handlers": ["handler"],
            "level": "INFO",
        },
        "keyboards": {
            "handlers": ["handler"],
            "level": "INFO",
        },
        "monster_card": {
            "handlers": ["handler"],
            "level": "INFO",
        },
        "scraper": {
            "handlers": ["handler"],
            "level": "INFO",
        },
        "singleton_bot": {
            "handlers": ["handler"],
            "level": "INFO",
        },
        "utils": {
            "handlers": ["handler"],
            "level": "INFO",
        },
    },
    "formatters": {
        "formatter": {
            "format": ("%(asctime)s %(levelname)s %(funcName)s %(message)s")
        }
    },
}
