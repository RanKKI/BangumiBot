from enum import Enum
import os
from pathlib import Path
from typing import Union

PREFIX = "BANGUMI_"


class Env(Enum):
    CLIENT_TYPE = PREFIX + "CLIENT_TYPE"
    CLIENT_IP = PREFIX + "CLIENT_IP"
    CLIENT_PORT = PREFIX + "CLIENT_PORT"
    CLIENT_USERNAME = PREFIX + "CLIENT_USERNAME"
    CLIENT_PASSWORD = PREFIX + "CLIENT_PASSWORD"

    DOWNLOAD_FOLDER = PREFIX + "DOWNLOAD_FOLDER"
    CACHE_FOLDER = PREFIX + "CACHE_FOLDER"
    MEDIA_FOLDER = PREFIX + "MEDIA_FOLDER"

    REDIS_HOST = PREFIX + "REDIS_HOST"
    REDIS_PORT = PREFIX + "REDIS_PORT"
    REDIS_PASSWORD = PREFIX + "REDIS_PASSWORD"

    CHECK_INTERVAL = PREFIX + "CHECK_INTERVAL"

    CONFIG_PATH = PREFIX + "CONFIG_PATH"

    LOGGER_LEVEL = PREFIX + "LOGGER_LEVEL"

    # 是否持续做种
    SEEDING = PREFIX + "SEEDING"

    @staticmethod
    def get(key: "Env", default="", *, type: Union[str, bool, int, Path] = str) -> str:
        val = os.environ.get(key.value, default)
        if type == str:
            return val
        if type == int:
            return int(val)
        if type == bool:
            return val.lower() in ["yes", "true", "1"]
        if type == Path:
            return Path(val)
        raise ValueError(f"Unknown type: {type}")
