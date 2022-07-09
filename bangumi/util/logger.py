import logging

from .const import Env
import os

def setup_logger():
    # level = logging.DEBUG if settings.debug_mode else logging.INFO
    level = logging.getLevelName(os.environ.get(Env.LOGGER_LEVEL.value, "INFO"))
    DATE_FORMAT = "%Y-%m-%d %X"
    LOGGING_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
    logging.basicConfig(
        # filename=settings.log_path,
        # filemode="w",
        level=level,
        datefmt=DATE_FORMAT,
        format=LOGGING_FORMAT,
        encoding="utf-8",
    )
