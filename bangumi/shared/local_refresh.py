import logging
import os
from glob import glob
from pathlib import Path

import requests
from bangumi.consts.env import Env
from bangumi.downloader import DownloadState
from bangumi.parser import Parser

logger = logging.getLogger(__name__)


def refresh_local(redisDB, downloader):
    logger.info("refreshing local data...")
    media = Env.get(Env.MEDIA_FOLDER, "media", type=Path)
    exists = set()
    for item in glob(str(media / "**/*"), recursive=True):
        if not os.path.isfile(item):
            continue
        name, _ = os.path.splitext(os.path.basename(item))
        if redisDB.is_downloaded(name):
            continue
        exists.add(name)

    logger.info("Found %d files that already downloaded", len(exists))
    for name in exists:
        redisDB.set_downloaded(name)

    """
        恢复 Redis 中的正在做种的项目
        """
    if Env.get(Env.SEEDING, False, type=bool):
        try:
            completed = downloader.get_downloads(DownloadState.FINISHED)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to get completed torrents {e}")
            return

        for item in completed:
            try:
                info = Parser.parse_bangumi_name(item.name)
            except ValueError:
                logger.error(f"Failed to parse {item.name}")
                continue
            """
                已经被转移到 media 目录，但还存在于下载器中（且是已完成项目），认为是正在做种的项目
                """
            if redisDB.is_downloaded(info.formatted):
                redisDB.set_seeding(item.hash)
