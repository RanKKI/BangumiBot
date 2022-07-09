import logging
import os
from time import time

import redis

from bangumi.util.const import Env
from bangumi.rss import RSSItem

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

    def get(self, hash_: str) -> RSSItem | None:
        ret = self.client.hgetall(hash_)
        if not ret:
            return None
        return RSSItem(
            name=ret.get("name"),
            url=ret.get("url", ""),
            publish_at=int(ret.get("publish_at", "0")),
            hash=hash_,
        )

    def set(self, hash_: str, item: RSSItem) -> None:
        self.client.hset(hash_, "name", item.name)
        self.client.hset(hash_, "url", item.url)
        self.client.hset(hash_, "publish_at", item.publish_at)

    def remove(self, hash_: str) -> None:
        self.client.delete(hash_)

    def update_last_checked_time(self):
        self.client.set("last_checked_time", int(time()))

    def get_last_checked_time(self) -> int:
        return int(self.client.get("last_checked_time") or 0)
