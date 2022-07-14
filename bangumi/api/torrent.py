from typing import List

from bangumi.database import redisDB
from bangumi.entitiy import WaitDownloadItem
from pydantic import BaseModel

from .app import app as api


class AddTorrent(BaseModel):
    name: str
    url: str


@api.post("/add_torrent")
async def add_torrent(item: AddTorrent):
    redisDB.add_to_torrent_queue(WaitDownloadItem(item.name, item.url))
    return {"message": "OK!"}


@api.post("/add_torrents")
async def add_torrents(items: List[AddTorrent]):
    redisDB.add_to_torrent_queue(
        [WaitDownloadItem(item.name, item.url) for item in items]
    )
    return {"message": "OK!"}
