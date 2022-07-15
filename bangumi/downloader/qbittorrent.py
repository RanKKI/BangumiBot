import logging
from functools import wraps
from pathlib import Path
from typing import Any, List

from bangumi.entitiy import DownloadItem
from qbittorrentapi import APIConnectionError, Client, LoginFailed

from .downloader import Downloader, DownloadState

logger = logging.getLogger(__name__)


def handle_api_error(default_val: Any):
    def _inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except APIConnectionError as e:
                logger.error(
                    "[%s] Failed to connect to qBittorrent %s", func.__name__, e
                )

                if callable(default_val):
                    return default_val()

                return default_val

        return wrapper

    return _inner


class QBittorrentDownloader(Downloader):
    def __init__(self, **kwargs):
        super().__init__()

        host = kwargs.pop("host", "localhost")
        port = kwargs.pop("port", 6800)
        username = kwargs.pop("username", "")
        password = kwargs.pop("password", "")

        logger.info(f"QBitTorrent Connecting to {host}:{port}")

        self.client = Client(
            host=f"{host}:{port}",
            username=username,
            password=password,
        )

    def connect(self):
        try:
            self.client.auth_log_in()
            logger.info(f"qBittorrent: {self.client.app.version}")
            logger.info(f"qBittorrent Web API: {self.client.app.web_api_version}")
        except LoginFailed as e:
            logger.error(f"QBitTorrent Login Failed: {e}")

    @handle_api_error(False)
    def add_torrent_by_magnet(self, magnet: str) -> bool:
        return self.client.torrents_add(urls=[magnet]) == "Ok."

    @handle_api_error(False)
    def add_torrent_by_file(self, torrent_file: Path) -> bool:
        return self.client.torrents_add(torrent_files=[torrent_file]) == "Ok."

    @handle_api_error(False)
    def remove_torrent(self, item: DownloadItem) -> bool:
        self.client.torrents_delete(hashes=[item.hash])

    @handle_api_error(lambda: [])
    def get_downloads(self, state: int = DownloadState.NONE) -> List[DownloadItem]:
        resp = self.client.torrents_info()

        """

        all, downloading, completed, paused, active, inactive, resumed, stalled, stalled_uploading and stalled_downloading

        """

        def wrapper(item):
            hash = item["hash"]
            resp = self.client.torrents_files(torrent_hash=hash)
            files = [Path(x["name"]) for x in resp]
            return DownloadItem(hash=hash, name=item["name"], files=files)

        if state == DownloadState.NONE:
            return list(map(wrapper, resp))

        ret = []
        for item in resp:
            add = False
            if state & DownloadState.FINISHED and (
                item["state"] == "completed" or item["amount_left"] <= 0
            ):
                add = True
            if state & DownloadState.DOWNLOADING and item["state"] == "downloading":
                add = True
            if state & DownloadState.PAUSED and item["state"] == "paused":
                add = True

            if add:
                ret.append(item)

        return list(map(wrapper, ret))
