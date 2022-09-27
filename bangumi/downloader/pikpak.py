import logging
from functools import wraps
from typing import Any, List

from pikpakapi import PikPakApi, PikpakException, PikpakAccessTokenExpireException
from bangumi.entitiy import DownloadItem

from .downloader import Downloader

logger = logging.getLogger(__name__)


def handle_api_error(default_val: Any):
    def _inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except PikpakAccessTokenExpireException:
                this, *_ = args
                this.client.refresh_access_token()
                try:
                    func(*args, **kwargs)
                except PikpakException as e:
                    logger.error(f"Pikpak failed to download with error {e}")

                    if callable(default_val):
                        return default_val()

                    return default_val

        return wrapper

    return _inner


class PikpakDownloader(Downloader):
    def __init__(self, **kwargs):
        super().__init__()

        username = kwargs.pop("username", "")
        password = kwargs.pop("password", "")

        logger.info(f"Pikpak initializing...")

        self.client = PikPakApi(username, password)

    def connect(self):
        try:
            self.client.login()
            logger.info("Logined to pikpak")
        except Exception as e:
            logger.error(f"Pikpak failed to login: {e}")

    @handle_api_error(False)
    def add_torrent_by_magnet(self, magnet: str) -> bool:
        self.client.offline_download(magnet)
        return True

    @handle_api_error(False)
    def add_torrent_by_url(self, url: str) -> bool:
        self.client.offline_download(url)
        return True

    @handle_api_error(False)
    def add_torrent_by_file(self, torrent_file: str) -> bool:
        logger.error(f"Pikpak does not support with torrent file yet")
        return False

    def remove_torrent(self, item: DownloadItem) -> bool:
        # pikpak will automatically remove the torrent from its offline list
        return True

    def get_downloads(self, state: int = ...) -> List[DownloadItem]:
        # pikpakapi library does not support moving files yet
        return []
