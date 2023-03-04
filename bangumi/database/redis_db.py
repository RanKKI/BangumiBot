from hashlib import md5
import logging
import os
import re
from time import time
from typing import List, Union

import redis
from bangumi.consts.env import Env
from bangumi.entitiy import WaitDownloadItem
from bangumi.util import from_dict_to_dataclass

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
            host=Env.get(Env.REDIS_HOST, "localhost"),
            port=Env.get(Env.REDIS_PORT, "6379"),
            password=Env.get(Env.REDIS_PASSWORD, ""),
            decode_responses=True,
            socket_connect_timeout=5,
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
        if not self.client:
            return
        self.client.set("last_checked_time", int(time()))

    def get_last_checked_time(self) -> int:
        if not self.client:
            return 0
        return int(self.client.get("last_checked_time") or 0)

    def add_to_torrent_queue(
        self, items: Union[WaitDownloadItem, List[WaitDownloadItem]]
    ) -> None:
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

    async def get_pending(self) -> List[WaitDownloadItem]:
        """
        返回还未添加进下载队列
        """
        hash_arr = self.client.lrange("pool_list", 0, 50)
        return [self.get(hash_) for hash_ in hash_arr]

    def get_key_from_formatted_name(self, name: str) -> str:
        ret = re.match(r"(.*) (S\d+E\d+)", name.strip())
        if not ret:
            return
        name, ext = ret.groups()
        return name.strip().replace(" ", "_") + ":" + ext

    def is_downloaded(self, formatted_name: str) -> bool:
        key = self.get_key_from_formatted_name(formatted_name)
        if not key:
            return False
        return self.client.get(f"file:{key}")

    def set_downloaded(self, formatted_name: str):
        key = self.get_key_from_formatted_name(formatted_name)
        if not key:
            return
        self.client.set(f"file:{key}", 1)

    def is_seeding(self, _hash: str) -> bool:
        return self.client.get(f"seeding:{_hash}")

    def set_seeding(self, _hash: str) -> None:
        self.client.set(f"seeding:{_hash}", 1)

    def init(self) -> bool:
        if not self.client:
            return False
        if self.client.get("initd"):
            return False
        self.client.set("initd", 1)
        return True
