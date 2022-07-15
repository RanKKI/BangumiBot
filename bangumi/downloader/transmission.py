import logging
from functools import wraps
from pathlib import Path
from typing import Any, List

from transmission_rpc import Client, Torrent, TransmissionError

from bangumi.entitiy import DownloadItem

from .downloader import Downloader, DownloadState

logger = logging.getLogger(__name__)


def handle_api_error(default_val: Any):
    def _inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TransmissionError as e:
                logger.error(
                    "[%s] Failed to connect to Transmission %s", func.__name__, e
                )

                if callable(default_val):
                    return default_val()

                return default_val

        return wrapper

    return _inner


class TransmissionDownloader(Downloader):
    def __init__(self, **kwargs):
        super().__init__()

        host = kwargs.pop("host", "localhost")
        port = kwargs.pop("port", 6800)
        username = kwargs.pop("username", "")
        password = kwargs.pop("password", "")

        logger.info(f"Transmission Connecting to {host}:{port}")

        self.client = Client(
            host=f"{host}:{port}",
            username=username,
            password=password,
        )

    def connect(self):
        logger.info(f"Transmission: {'.'.join(map(str, self.client.server_version))}")
        logger.info(f"Transmission RPC: {self.client.rpc_version}")

    @handle_api_error(False)
    def add_torrent_by_magnet(self, magnet: str) -> bool:
        return self.client.add_torrent(magnet)

    @handle_api_error(False)
    def add_torrent_by_file(self, torrent_file: Path) -> bool:
        return self.client.add_torrent(torrent_file)

    @handle_api_error(False)
    def remove_torrent(self, item: DownloadItem) -> bool:
        self.client.remove_torrent(ids=item.hash)

    @handle_api_error(lambda: [])
    def get_downloads(self, state: int = DownloadState.NONE) -> List[DownloadItem]:
        resp = self.client.get_torrents()

        def wrapper(item: Torrent):
            return DownloadItem(
                hash=item.hashString,
                name=item.name,
                files=[Path(x.name) for x in item.files()],
            )

        if state == DownloadState.NONE:
            return list(map(wrapper, resp))

        ret = []
        for item in resp:
            add = False
            if state & DownloadState.FINISHED and item.progress >= 100:
                add = True
            if state & DownloadState.DOWNLOADING and (
                item.status.download_pending or item.status.downloading
            ):
                add = True
            if state & DownloadState.PAUSED and item.status.stopped:
                add = True

            if add:
                ret.append(item)

        return list(map(wrapper, ret))
