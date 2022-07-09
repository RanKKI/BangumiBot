import logging
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from bangumi.database import redisDB
from bangumi.downloader import Downloader, build_downloader
from bangumi.rss.rss_parser import RSSItem

logger = logging.getLogger(__name__)

class AddTorrent(BaseModel):
    name: str
    url: str
    hash: str


app = FastAPI()
downloader: Downloader

@app.post("/add")
async def read_item(info: AddTorrent):
    downloader.add_torrent(info.url)
    redisDB.set(info.hash, RSSItem(
        name=info.name,
        url=info.url,
        hash=info.hash,
        publish_at=0
    ))
    return {"message": "OK!"}

load_dotenv(".env")
downloader = build_downloader()
redisDB.connect()