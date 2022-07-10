import logging

from .const import Env
import os


def setup_logger():
    level = logging.getLevelName(
        os.environ.get(
            Env.LOGGER_LEVEL.value,
            "INFO"))
    DATE_FORMAT = "%Y-%m-%d %X"
    LOGGING_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
    logging.basicConfig(
        filename="./output.log",
        filemode="w",
        level=level,
        datefmt=DATE_FORMAT,
        format=LOGGING_FORMAT,
        encoding="utf-8",
    )
