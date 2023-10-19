"""The module enables `loguru` logging by intercepting the logs coming to the `logging` module."""

import logging

from loguru import logger

logger.add("logs/{time}.log", encoding="utf-8", rotation="00:00")


class InterceptHandler(logging.Handler):
    """The `logging` logs interceptor."""

    def emit(self, record):
        """Intercept the `logging` logs and redirect them to `loguru`."""
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=0)
