import logging
import os
import sys
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from bangumi.database import redisDB
from bangumi.downloader import Downloader, build_downloader
from bangumi.rss.rss import RSS
from bangumi.rss.rss_parser import RSSItem
from bangumi.util import setup_env

logger = logging.getLogger(__name__)

class AddTorrent(BaseModel):
    name: str
    url: str
    hash: str


app = FastAPI()
downloader: Downloader

@app.post("/add_torrent")
async def read_item(info: AddTorrent):
    downloader.add_torrent(info.url)
    redisDB.set(info.hash, RSSItem(
        name=info.name,
        url=info.url,
        hash=info.hash,
        publish_at=0
    ))
    return {"message": "OK!"}

@app.post("/add_torrents")
async def read_item(infos: List[AddTorrent]):
    for info in infos:
        downloader.add_torrent(info.url)
        redisDB.set(info.hash, RSSItem(
            name=info.name,
            url=info.url,
            hash=info.hash,
            publish_at=0
        ))
    return {"message": "OK!"}


class AddRss(BaseModel):
    url: str

@app.post("/add_by_rss")
async def read_item(r: AddRss):
    for item in RSS().scrape_url(r.url):
        downloader.add_torrent(item.url)
        redisDB.set(item.hash, RSSItem(
            name=item.name,
            url=item.url,
            hash=item.hash,
            publish_at=item.publish_at
        ))
    return {"message": "OK!"}

if not os.environ.get("TEST_ENV") and not sys.argv[0] == "main.py":
    """
    GitHub CI/CD 中不执行
    """
    setup_env()
    downloader = build_downloader()
    redisDB.connect()
