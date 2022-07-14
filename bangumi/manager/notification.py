import json
import logging
import os
from subprocess import DEVNULL, STDOUT, check_call

from typing import List

logger = logging.getLogger(__name__)


class Notification(object):
    def __init__(self) -> None:
        self.callbacks: List[str] = []

    def load_config(self, config_path: str):
        if not os.path.exists(config_path):
            return
        with open(config_path, "r") as f:
            data = json.load(f)
        self.callbacks = data

    def call(self, title: str):
        logger.info(f"Send notification: {title}")
        for callback in self.callbacks:
            self.__call(callback, title)

    def __call(self, callback: str, title: str):
        if callback.startswith("http"):
            self.__call_http(callback.format(title=title))
        elif os.path.exists(callback):
            self.__call_script(callback, title)

    def __call_http(self, url: str):
        check_call(["curl", "-X", "GET", url], stdout=DEVNULL, stderr=STDOUT)

    def __call_script(self, script: str, title: str):
        check_call([script, title], stdout=DEVNULL, stderr=STDOUT)
