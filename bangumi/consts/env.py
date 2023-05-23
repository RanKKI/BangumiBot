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

    OPENAI_API_KEY = PREFIX + "OPENAI_API_KEY"

    @staticmethod
    def get(
        key: "Env", default="", *, valueType: Union[str, bool, int, Path] = str
    ) -> str:
        val = os.environ.get(key.value, default)
        if valueType == str:
            return val
        if valueType == int:
            return int(val)
        if valueType == bool:
            if type(val) == bool:
                return val
            return val.lower() in ["yes", "true", "1"]
        if valueType == Path:
            return Path(val)
        raise ValueError(f"Unknown type: {valueType}")

    @staticmethod
    def as_table():
        def env(key: Env, default=""):
            return Env.get(key, default, valueType=str)

        return [
            ["Log Level", env(Env.LOGGER_LEVEL)],
            ["Client", env(Env.CLIENT_TYPE)],
            [
                "Client Addr",
                f"{env(Env.CLIENT_USERNAME)}:{env(Env.CLIENT_PASSWORD)}@{env(Env.CLIENT_IP)}:{env(Env.CLIENT_PORT)}",
            ],
            [
                "Redis",
                f"{env(Env.REDIS_PASSWORD)}@{env(Env.REDIS_HOST)}:{env(Env.REDIS_PORT)}",
            ],
            ["Check", env(Env.CHECK_INTERVAL)],
            ["Download", env(Env.DOWNLOAD_FOLDER)],
            ["Cache", env(Env.CACHE_FOLDER)],
            ["Media", env(Env.MEDIA_FOLDER)],
            ["Config", env(Env.CONFIG_PATH)],
            ["Seeding", Env.get(Env.SEEDING, False, valueType=bool)],
            ["OpenAI Key", "***"],
        ]
