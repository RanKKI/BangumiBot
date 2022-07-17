import json
import logging
import os
import shlex
from subprocess import DEVNULL, STDOUT, check_call, check_output
from typing import List

from requests.utils import requote_uri

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
        result = []
        for callback in self.callbacks:
            ext = {}

            if isinstance(callback, dict):
                ext = callback
                callback = callback.pop("url")

            r = None
            try:
                if callback.startswith("http"):
                    r = self.call_http(callback, title=title, **ext)
                elif os.path.exists(callback):
                    r = self.call_script(callback, title)
            except Exception as e:
                logger.error(f"Failed to call {callback}: {e}")

            result.append(r)

        return result


    def call_http(self, url: str, title: str, **kwargs):
        method = kwargs.get("method", "GET")
        data = kwargs.get("data", {})
        data["title"] = title
        url = requote_uri(url.format(title=title))
        if method == "GET":
            cmd = ["curl", "-s", "-X", "GET", url]
        elif method == "POST":
            cmd = [
                "curl",
                "-s",
                "-X",
                "POST",
                "--data",
                json.dumps(data),
                "-H",
                "Content-Type:application/json",
                url,
            ]
        else:
            return
        return self.__call(cmd)

    def call_script(self, script: str, title: str):
        return self.__call(shlex.split(script) + [title])

    def __call(self, cmd: List[str]):
        if os.environ.get("TEST_ENV"):
            return check_output(cmd)
        logger.debug(f"Call: {cmd}")
        check_call(cmd, stdout=DEVNULL, stderr=STDOUT)
