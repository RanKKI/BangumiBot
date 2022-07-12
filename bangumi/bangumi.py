
import logging
import os
from time import sleep, time


from bangumi.database import redisDB
from bangumi.downloader import DownloadState, downloader
from bangumi.entitiy import DownloadItem, WaitDownloadItem
from bangumi.parser import Parser
from bangumi.rss import RSS
from bangumi.util import Env, move_file, get_relative_path, safe_call

logger = logging.getLogger(__name__)


class Bangumi(object):

    def __init__(self) -> None:
        super().__init__()
        self.rss = RSS(urls=[
            # "https://dmhy.org/topics/rss/rss.xml"
            "https://mikanani.me/RSS/MyBangumi?token=2O6Rl47PH1mXSw6v3ACwCA%3d%3d"
        ])
        self.parser = Parser()

    def rename(self, item: DownloadItem, info: WaitDownloadItem) -> bool:
        logger.info(f"Renaming {item.hash} {item.name}...")
        if item.hash != info.hash:
            logger.error(f"Hash mismatch {item.hash} {info.hash}")
            return False
        if len(item.files) > 1:
            logger.error(f"Can't rename multi-file torrent {item.hash}")
            return False
        if len(item.files) == 0:
            logger.error(f"Can't rename empty torrent {item.hash}")
            return False

        file = item.files[0]
        file = get_relative_path(file)

        if not file.exists():
            logger.error(f"File {file} doesn't exist")
            return False

        result = self.parser.analyse(info.name)
        logger.info(f"Renaming {file.name} to {result.formatted}")
        try:
            move_file(file, result)
            return True
        except Exception as e:
            logger.error(f"Failed to rename {e}")
        return False

    def on_torrent_finished(self, item: DownloadItem):
        ret = self.rename(item, redisDB.get(item.hash))
        if not ret:
            return
        redisDB.remove(item.hash)
        downloader.remove_torrent(item)

    @safe_call
    def check(self, last_dt: int):
        logger.info("Checking RSS...")
        items = self.rss.scrape(last_dt)
        logger.info("Found %d items", len(items))
        redisDB.add_to_torrent_queue(items)

    @safe_call
    def check_complete(self):
        logger.debug("Checking complete...")
        completed = downloader.get_downloads(DownloadState.FINISHED)
        if len(completed) == 0:
            return
        logger.info("Found %d completed downloads", len(completed))
        for item in completed:
            self.on_torrent_finished(item)

    @safe_call
    def check_queue(self):
        logger.debug("Checking torrent queue...")
        count = 0
        item = redisDB.pop_torrent_to_download()
        while item:
            downloader.add_torrent(item.url)
            logger.info(f"Added {item.url} to downloader")
            item = redisDB.pop_torrent_to_download()
            count += 1
        if count > 0:
            logger.info("Added %d torrents to downloader", count)

    def loop(self):
        INTERVAL = int(os.environ.get(Env.CHECK_INTERVAL.value, 60 * 10))

        while True:
            current = int(time())
            last = redisDB.get_last_checked_time()
            if current - last > INTERVAL:
                self.check(last)
                redisDB.update_last_checked_time()
            self.check_complete()
            self.check_queue()
            sleep(10)

    def init(self):
        pass
        # media = Path(os.environ.get(Env.MEDIA_FOLDER.value, "media"))
        # for item in media.glob("**/*"):
        #     if not item.is_file():
        #         continue
        #     # get name without ext
        #     name, _ = os.path.splitext(item.name)
        #     redisDB.set_downloaded(name)

    def run(self):
        logger.info("Starting...")
        redisDB.connect()
        downloader.connect()
        if redisDB.init():
            self.init()
        self.loop()
