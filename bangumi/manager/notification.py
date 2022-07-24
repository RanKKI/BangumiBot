import json
import logging
import os
import shlex
from subprocess import DEVNULL, STDOUT, check_call, check_output
from typing import List

from bangumi.entitiy import Configurable
from requests.utils import requote_uri
from tabulate import tabulate

logger = logging.getLogger(__name__)


class Notification(Configurable):
    def __init__(self) -> None:
        self.callbacks: List[str] = []

    def load_config(self, data):
        self.callbacks = data
        self.log_config()

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

    def log_config(self):
        table = []
        for callback in self.callbacks:
            ext = {}
            if isinstance(callback, dict):
                ext = callback
                callback = callback.pop("url")

            if callback.startswith("http"):
                table.append(["HTTP", ext.get("method", "GET"), callback])
            else:
                table.append(["SHELL", "", callback])

        logger.info("Notification")
        r = tabulate(
            table,
            headers=["Type", "Method", "URi"],
            tablefmt="simple",
        )

        for line in r.splitlines():
            logger.info(line)
        logger.info("")
