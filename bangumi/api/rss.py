from bangumi.database import redisDB
from bangumi.rss import RSS
from pydantic import BaseModel

from .app import app as api


class AddRss(BaseModel):
    url: str


@api.post("/add_by_rss")
async def add_torrents_by_rss(r: AddRss):
    items = await RSS().scrape_url(r.url)
    redisDB.add_to_torrent_queue(items)
    return {"message": "OK!", "items": items}
