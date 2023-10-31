log_config = {
    "version": 1,
    "handlers": {
        "handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "formatter",
            "filename": "armor_class_bot.log",
            "mode": "a",
            "maxBytes": 1000000,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "armor_class_bot": {
            "handlers": ["handler"],
            "level": "DEBUG",
        },
        "exception_routes": {
            "handlers": ["handler"],
            "level": "DEBUG",
        },
        "keyboards": {
            "handlers": ["handler"],
            "level": "DEBUG",
        },
        "monster_card": {
            "handlers": ["handler"],
            "level": "DEBUG",
        },
        "scraper": {
            "handlers": ["handler"],
            "level": "DEBUG",
        },
        "singleton_bot": {
            "handlers": ["handler"],
            "level": "DEBUG",
        },
        "utils": {
            "handlers": ["handler"],
            "level": "DEBUG",
        },
    },
    "formatters": {
        "formatter": {
            "format": ("%(asctime)s %(levelname)s %(funcName)s %(message)s")
        }
    },
}
