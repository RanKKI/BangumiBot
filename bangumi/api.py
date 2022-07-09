import logging
import os
from typing import List
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from bangumi.database import redisDB
from bangumi.downloader import Downloader, build_downloader
from bangumi.rss.rss import RSS
from bangumi.rss.rss_parser import RSSItem

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
    for item in RSS(urls=[]).scrape_url(r.url):
        downloader.add_torrent(item.url)
        redisDB.set(item.hash, RSSItem(
            name=item.name,
            url=item.url,
            hash=item.hash,
            publish_at=item.publish_at
        ))
    return {"message": "OK!"}

if not os.environ.get("GITHUB_ACTIONS"):
    """
    GitHub CI/CD 中不执行
    """
    load_dotenv(".env")
    downloader = build_downloader()
    redisDB.connect()