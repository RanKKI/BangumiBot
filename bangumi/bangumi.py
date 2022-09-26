import asyncio
import logging
import os
import signal
import threading
from time import sleep, time

import requests
from tabulate import tabulate

from bangumi.database import redisDB
from bangumi.downloader import DownloadState, downloader
from bangumi.entitiy import DownloadItem, WaitDownloadItem
from bangumi.manager import ConfigManager, Notification
from bangumi.parser import Parser
from bangumi.rss import RSS
from bangumi.shared import refresh_local
from bangumi.util import Env, get_relative_path, move_file, safe_call

logger = logging.getLogger(__name__)


class Bangumi(object):
    def __init__(self) -> None:
        super().__init__()
        self.rss = RSS()
        self.notification = Notification()
        self.config = ConfigManager()
        self.is_running = False

    def rename(self, item: DownloadItem, info: WaitDownloadItem) -> str:
        logger.info(f"Renaming {item.hash} {item.name}...")
        if item.hash != info.hash:
            logger.error(f"Hash mismatch {item.hash} {info.hash}")
            return
        if len(item.files) > 1:
            logger.error(f"Can't rename multi-file torrent {item.hash}")
            return
        if len(item.files) == 0:
            logger.error(f"Can't rename empty torrent {item.hash}")
            return

        file = item.files[0]
        file = get_relative_path(file)

        if not file.exists():
            logger.error(f"File {file} doesn't exist")
            return

        try:
            result = Parser.parse_bangumi_name(info.name)
            logger.info(f"Renaming {file.name} to {result.formatted}")
            seeding = Env.get(Env.SEEDING, False, type=bool)
            move_file(file, result, seeding=seeding)
            return result.formatted, seeding
        except Exception as e:
            logger.error(f"Failed to rename {e}")

    def on_torrent_finished(self, item: DownloadItem):
        ret = self.rename(item, redisDB.get(item.hash))
        if not ret:
            return
        title, seeding = ret
        redisDB.remove(item.hash)
        if seeding:
            redisDB.set_seeding(item.hash)
        else:
            downloader.remove_torrent(item)
        self.notification.call(title)

    @safe_call
    async def check(self, last_dt: int):
        logger.debug("Checking RSS...")
        items = await self.rss.scrape(last_dt)
        if not items:
            return
        logger.info("Found %d items", len(items))
        redisDB.add_to_torrent_queue(items)

    @safe_call
    def check_complete(self):
        logger.debug("Checking complete...")
        try:
            completed = downloader.get_downloads(DownloadState.FINISHED)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to get completed torrents {e}")
            return

        # 过滤标记为做种的已完成项目
        completed = [item for item in completed if not redisDB.is_seeding(item.hash)]

        if len(completed) == 0:
            return

        logger.info("Found %d completed downloads", len(completed))
        for item in completed:
            self.on_torrent_finished(item)

    @safe_call
    def check_queue(self):
        logger.debug("Checking torrent queue...")
        count, failed_count = 0, 0
        failed_added = []
        while True:
            item = redisDB.pop_torrent_to_download()
            if not item:
                break

            try:
                info = Parser.parse_bangumi_name(item.name)
            except ValueError:
                failed_count += 1
                logger.error(f"Failed to parse {item.name}")
                continue

            if redisDB.is_downloaded(info.formatted):  # 已经下载过了
                redisDB.remove(item.hash)
                continue

            try:
                success_added = downloader.add_torrent(item.url)
            except Exception as e:
                success_added = False
                failed_count += 1
                logger.error(e)

            if not success_added:
                failed_added.append(item)
                logger.error(
                    f"Failed to add torrent {info.formatted}, will retry later"
                )
                continue

            redisDB.set_downloaded(info.formatted)
            logger.info(f"Added [{info.formatted}] to downloader")
            count += 1

        if count > 0:
            logger.info(f"Added {count} torrents to downloader")

        if failed_count > 0:
            logger.error(f"Failed to add {failed_count} torrents to downloader")

        if failed_added:
            redisDB.add_to_torrent_queue(failed_added)
            logger.info(f"Added {len(failed_added)} failed torrents to queue")

    async def loop(self):
        INTERVAL = Env.get(Env.CHECK_INTERVAL, 60 * 10, type=int)

        while self.is_running:
            current = int(time())
            last = redisDB.get_last_checked_time()
            if current - last > INTERVAL:
                await self.check(last)
                redisDB.update_last_checked_time()
            self.check_complete()
            self.check_queue()
            sleep(30)

    def load_config(self):
        self.config.register("rss.json", self.rss)
        self.config.register("notification.json", self.notification)
        self.config.start_listener()

    def log_env(self):
        r = tabulate(Env.as_table(), headers=["Env", ""], tablefmt="simple")
        for line in r.splitlines():
            logger.info(line)
        logger.info("")

    def run(self):
        self.is_running = True
        logger.info("Starting...")
        self.load_config()
        if redisDB.init():
            refresh_local(redisDB, downloader)
        self.log_env()
        asyncio.run(self.loop())

    def stop(self):
        logger.info("Stopping...")
        self.is_running = False
        self.config.stop_listener()


class BangumiBackgroundTask(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.bangumi = Bangumi()
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def run(self):
        try:
            self.bangumi.run()
        except Exception as e:
            logger.exception(e)
            os._exit(1)

    def stop(self, *args, **kwargs):
        self.bangumi.stop()
