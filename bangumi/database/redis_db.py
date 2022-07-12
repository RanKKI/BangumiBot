import logging
import os
from time import time
from typing import List, Union

import redis
from bangumi.consts.env import Env
from bangumi.entitiy import WaitDownloadItem
from bangumi.util.data_class import from_dict_to_dataclass

logger = logging.getLogger(__name__)


class RedisDB(object):

    def __init__(self) -> None:
        self.client: redis.Redis = None

    def connect(self) -> None:
        if self.client is not None:
            logger.debug("RedisDB already connected")
            return
        logger.info("Connecting to Redis...")
        self.client = redis.Redis(
            host=os.environ.get(Env.REDIS_HOST.value, "localhost"),
            port=os.environ.get(Env.REDIS_PORT.value, "6379"),
            password=os.environ.get(Env.REDIS_PASSWORD.value, ""),
            decode_responses=True
        )
        ret = self.client.info()
        logger.info(f"Connected to Redis, version {ret['redis_version']}")

    def get(self, hash_: str) -> WaitDownloadItem:
        ret = self.client.hgetall(hash_)
        if not ret:
            return None
        return from_dict_to_dataclass(WaitDownloadItem, ret)

    def remove(self, hash_: str) -> None:
        self.client.delete(hash_)

    def update_last_checked_time(self):
        self.client.set("last_checked_time", int(time()))

    def get_last_checked_time(self) -> int:
        return int(self.client.get("last_checked_time") or 0)

    def add_to_torrent_queue(self, items: Union[WaitDownloadItem, List[WaitDownloadItem]]) -> None:
        if isinstance(items, WaitDownloadItem):
            items = [items]
        for item in items:
            self.client.rpush("pool_list", item.hash)
            self.client.hset(item.hash, mapping=item.__dict__)

    def pop_torrent_to_download(self) -> WaitDownloadItem:
        hash_ = self.client.lpop("pool_list")
        if not hash_:
            return None
        return self.get(hash_)

    # def is_downloaded(self, formatted_name: str) -> bool:
    #     name_hash = md5(formatted_name.encode("utf-8")).hexdigest()
    #     return self.client.get(f"downloaded:file:{name_hash}")

    # def set_downloaded(self, formatted_name: str) -> bool:
    #     name_hash = md5(formatted_name.encode("utf-8")).hexdigest()
    #     self.client.set(f"downloaded:file:{name_hash}", 1)

    def init(self) -> bool:
        if self.client.get("initd"):
            return False
        self.client.set("initd", 1)
        return True