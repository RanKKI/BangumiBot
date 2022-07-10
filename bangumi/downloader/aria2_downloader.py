import json
import logging
from typing import List

import requests
from aria2p import API, Client, Download

from .downloader import Downloader, DownloadItem, DownloadState


logger = logging.getLogger(__name__)

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
            self.client.get_stats()
        except Exception:
            logger.error("Aria2 failed to connect")

    def __wrap_aria2_item(self, item: Download) -> DownloadItem:
        files = [x.path for x in item.files]
        return DownloadItem(id=item.info_hash, name=item.name, files=files)

    def add_torrent_by_magnet(self, magnet: str) -> DownloadItem:
        item = self.client.add_magnet(magnet)
        return self.__wrap_aria2_item(item)

    def add_torrent_by_file(self, torrent_file: str) -> DownloadItem:
        item = self.client.add_torrent(torrent_file)
        return self.__wrap_aria2_item(item)

    def remove_torrent(self, item: DownloadItem) -> bool:
        try:
            downloads = self.client.get_downloads()
        except Exception:
            logger.error("Failed to remove torrent")
            return False

        targets = [
            download for download in downloads if download.info_hash == item.id]

        if len(targets) == 0:
            return False

        if len(targets) > 1:
            raise Exception("Multiple downloads with same id found")

        return all(self.client.remove(targets, force=True, clean=True))

    def get_downloads(self, state: DownloadState = ...) -> List[DownloadItem]:
        try:
            downloads = self.client.get_downloads()
        except Exception:
            logger.error("Failed to get downloads")
            return []

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
