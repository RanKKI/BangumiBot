from functools import wraps
import json
import logging
from typing import Any, List

from aria2p import API, Client, Download, ClientException

from .downloader import Downloader, DownloadItem, DownloadState


logger = logging.getLogger(__name__)

def handle_api_error(default_val: Any):

    def _inner(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ClientException:
                logger.error("[%s] Failed to connect to aria2", func.__name__)

                if callable(default_val):
                    return default_val()

                return default_val

        return wrapper

    return _inner

class Aria2Downloader(Downloader):

    def __init__(self, **kwargs):
        super().__init__()

        host = kwargs.pop('host', 'localhost')
        if not host.startswith('http'):
            host = 'http://' + host

        port = kwargs.pop('port', 6800)
        secret = kwargs.pop('secret', '')

        logger.info(f"Aria2 Connecting to {host}:{port}")

        self.client = API(
            Client(
                host=host,
                port=port,
                secret=secret
            )
        )

        try:
            ver = self.client.client.get_version()
            if isinstance(ver, dict):
                logger.info("Connected to aria2: %s", ver['version'])
            else:
                logger.info("Connected to aria2: %s", ver)
        except Exception as e:
            logger.error(f"Aria2 failed to connect {e}")

    def __wrap_aria2_item(self, item: Download) -> DownloadItem:
        files = [x.path for x in item.files]
        return DownloadItem(
            id=item.info_hash,
            name=item.name,
            files=files
        )

    @handle_api_error(False)
    def add_torrent_by_magnet(self, magnet: str) -> bool:
        self.client.add_magnet(magnet)

    @handle_api_error(False)
    def add_torrent_by_file(self, torrent_file: str) -> bool:
        self.client.add_torrent(torrent_file)

    @handle_api_error(False)
    def remove_torrent(self, item: DownloadItem) -> bool:
        downloads = self.client.get_downloads()

        targets = [download for download in downloads if download.info_hash == item.id]

        if len(targets) == 0:
            return False

        if len(targets) > 1:
            raise Exception("Multiple downloads with same id found")

        return all(self.client.remove(targets, force=True, clean=True))

    @handle_api_error(lambda: [])
    def get_downloads(self, state: DownloadState = ...) -> List[DownloadItem]:
        downloads = self.client.get_downloads()

        if state == DownloadState.NONE:
            return [self.__wrap_aria2_item(download) for download in downloads]

        ret = []

        for download in downloads:
            add = False
            if state == DownloadState.DOWNLOADING:
                if download.status == "active" and download.completed_length < download.total_length:
                    add = True
            elif state == DownloadState.FINISHED:
                if download.status == "complete":
                    add = True
                if download.status == "active" and download.completed_length == download.total_length:
                    add = True
            elif state == DownloadState.ERROR and download.status == "error":
                add = True

            if add:
                ret.append(self.__wrap_aria2_item(download))

        return ret
