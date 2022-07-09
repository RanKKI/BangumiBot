import os

from bangumi.util.const import Env

from .aria2_downloader import Aria2Downloader
from .downloader import Downloader, DownloadItem, DownloadState


def build_downloader() -> Downloader:
    client_type = os.environ.get(Env.CLIENT_TYPE.value, None)
    if client_type == "aria2":
        return Aria2Downloader(
            host=os.environ.get(Env.CLIENT_IP.value, None),
            port=os.environ.get(Env.CLIENT_PORT.value, None),
            secret=os.environ.get(Env.CLIENT_PASSWORD.value, None)
        )
    raise ValueError("Client type not specified")
