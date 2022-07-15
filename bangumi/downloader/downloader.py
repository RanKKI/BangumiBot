import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from hashlib import md5
from pathlib import Path
from typing import Callable, List

import requests
from bangumi.consts.env import Env
from bangumi.entitiy import DownloadItem

logger = logging.getLogger(__name__)


class DownloadState:
    NONE = 1 << 0
    DOWNLOADING = 1 << 1
    PAUSED = 1 << 2
    FINISHED = 1 << 3
    ERROR = 1 << 4


TorrentFinishedCB = Callable[[DownloadItem], None]


class Downloader(ABC):
    def __init__(self):
        self.on_torrent_finished_callback: TorrentFinishedCB = None
        self.cache_folder = Path(os.environ.get(Env.CACHE_FOLDER.value, ".cache"))

    def add_torrent(self, url_or_magnet: str) -> bool:
        logger.debug(f"Adding torrent {url_or_magnet}")
        if url_or_magnet.startswith("magnet:"):
            return self.add_torrent_by_magnet(url_or_magnet)
        if url_or_magnet.startswith("http"):
            return self.add_torrent_by_url(url_or_magnet)

        logger.error(f"Invalid url or magnet: {url_or_magnet}")
        return False

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
    def connect(self):
        pass

    @abstractmethod
    def add_torrent_by_magnet(self, magnet: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def add_torrent_by_file(self, torrent_file: Path) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def remove_torrent(self, item: DownloadItem) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def get_downloads(self, state: int = DownloadState.NONE) -> List[DownloadItem]:
        raise NotImplementedError()
