
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from hashlib import md5
from pathlib import Path
from typing import Callable, List

import requests
from bangumi.util.const import Env

logger = logging.getLogger(__name__)


@dataclass
class DownloadItem:
    id: str  # torrent hash
    name: str
    files: List[Path]

    def __eq__(self, other):
        if not isinstance(other, DownloadItem):
            raise TypeError("Can't compare DownloadItem with {}".format(type(other)))
        return self.id == other.id


class DownloadState(Enum):
    NONE = 0
    DOWNLOADING = 1
    PAUSED = 2
    FINISHED = 3
    ERROR = 4


TorrentFinishedCB = Callable[[DownloadItem], None]


class Downloader(ABC):

    def __init__(self):
        self.on_torrent_finished_callback: TorrentFinishedCB = None
        self.cache_folder = Path(
            os.environ.get(Env.CACHE_FOLDER.value, ".cache"))

    def add_torrent(self, url_or_magnet: str) -> bool:
        logger.debug(f"Adding torrent {url_or_magnet}")
        if url_or_magnet.startswith("magnet:"):
            return self.add_torrent_by_magnet(url_or_magnet)
        if url_or_magnet.startswith("http"):
            return self.add_torrent_by_url(url_or_magnet)

        raise ValueError("Invalid url or magnet: {}".format(url_or_magnet))

    def add_torrent_by_url(self, url: str) -> bool:
        file_data = requests.get(url)
        file_name = md5(url.encode()).hexdigest() + ".torrent"
        file_path = self.cache_folder / file_name
        if not file_path.exists():
            logger.debug(f"Saving torrent file to {file_path} from {url}")
            with open(file_path, "wb") as f:
                f.write(file_data.content)
        return self.add_torrent_by_file(file_path)

    @abstractmethod
    def add_torrent_by_magnet(self, magnet: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def add_torrent_by_file(self, torrent_file: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def remove_torrent(self, item: DownloadItem) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def get_downloads(
            self,
            state: DownloadState = DownloadState.NONE) -> List[DownloadItem]:
        raise NotImplementedError()
