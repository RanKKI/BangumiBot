from turtle import down
from typing import List

from aria2p import API, Client, Download

from .downloader import Downloader, DownloadItem, DownloadState


class Aria2Downloader(Downloader):

    def __init__(self, **kwargs):
        super().__init__()

        assert 'host' in kwargs, 'Aria2Downloader requires host'
        assert 'port' in kwargs, 'Aria2Downloader requires port'
        assert 'secret' in kwargs, 'Aria2Downloader requires secret'

        kwargs.pop("downloader_url", None)
        self.client = API(
            Client(
                host=kwargs.pop('host'),
                port=kwargs.pop('port'),
                secret=kwargs.pop('secret')
            )
        )

    def __wrap_aria2_item(self, item: Download) -> DownloadItem:
        files = [x.path for x in item.files]
        return DownloadItem(id=item.info_hash, name=item.name, files=files)

    def on_download_complete(self, gid: str):
        item = self.client.get_download(gid)
        self._on_torrent_finished(
            self.__wrap_aria2_item(item)
        )

    def add_torrent_by_magnet(self, magnet: str) -> DownloadItem:
        item = self.client.add_magnet(magnet)
        return self.__wrap_aria2_item(item)

    def add_torrent_by_file(self, torrent_file: str) -> DownloadItem:
        item = self.client.add_torrent(torrent_file)
        return self.__wrap_aria2_item(item)

    def remove_torrent(self, item: DownloadItem) -> bool:
        downloads = self.client.get_downloads()
        targets = [
            download for download in downloads if download.info_hash == item.id]

        if len(targets) == 0:
            return False

        if len(targets) > 1:
            raise Exception("Multiple downloads with same id found")

        return all(self.client.remove(targets, force=True, clean=True))

    def get_downloads(self, state: DownloadState = ...) -> List[DownloadItem]:
        downloads = self.client.get_downloads()
        ret = []

        for download in downloads:
            add = False
            if state == DownloadState.NONE:
                add = True
            elif state == DownloadState.DOWNLOADING:
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
