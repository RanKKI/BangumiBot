import os
from bangumi.consts.env import Env
from bangumi.util import setup_env

from .aria2 import Aria2Downloader
from .downloader import Downloader, DownloadState
from .qbittorrent import QBittorrentDownloader
from .transmission import TransmissionDownloader


def build_downloader() -> Downloader:

    client_type = os.environ.get(Env.CLIENT_TYPE.value, None)
    host = os.environ.get(Env.CLIENT_IP.value, None)
    port = os.environ.get(Env.CLIENT_PORT.value, None)
    username = os.environ.get(Env.CLIENT_USERNAME.value, None)
    password = os.environ.get(Env.CLIENT_PASSWORD.value, None)

    if client_type == "aria2":
        return Aria2Downloader(host=host, port=port, secret=password)
    elif client_type == "qbittorrent" or client_type == "qb":
        return QBittorrentDownloader(
            host=host, port=port, username=username, password=password
        )
    elif client_type == "transmission":
        return TransmissionDownloader(
            host=host, port=port, username=username, password=password
        )
    raise ValueError("Client type not specified")


downloader: Downloader = None

if not os.environ.get("TEST_ENV"):
    setup_env()
    downloader = build_downloader()
