import logging
import os
import sys
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from bangumi.database import redisDB
from bangumi.entitiy import WaitDownloadItem
from bangumi.rss import RSS
from bangumi.util import setup_env

logger = logging.getLogger(__name__)

class AddTorrent(BaseModel):
    name: str
    url: str

class AddRss(BaseModel):
    url: str

app = FastAPI()

@app.post("/add_torrent")
async def add_torrent(item: AddTorrent):
    print(item)
    redisDB.add_to_torrent_queue(WaitDownloadItem(item.name, item.url))
    return {"message": "OK!"}

@app.post("/add_torrents")
async def add_torrents(items: List[AddTorrent]):
    redisDB.add_to_torrent_queue([WaitDownloadItem(item.name, item.url) for item in items])
    return {"message": "OK!"}

@app.post("/add_by_rss")
async def add_torrents_by_rss(r: AddRss):
    items = await RSS().scrape_url(r.url)
    redisDB.add_to_torrent_queue(items)
    return {"message": "OK!", "count": items}

@app.on_event("startup")
def startup():
    setup_env()
    redisDB.connect()