from pydantic import BaseModel

from bangumi.database import redisDB
from bangumi.entitiy import RSSSite
from bangumi.manager import ConfigManager
from bangumi.rss import RSS

from .app import app as api


class AddRss(BaseModel):
    url: str


@api.post("/add_by_rss")
async def add_torrents_by_rss(r: AddRss):
    config = ConfigManager()
    rss = RSS()
    config.register("rss.json", rss)
    config.load_config()

    items = await rss.scrape_url(RSSSite(url=r.url))
    # redisDB.add_to_torrent_queue(items)
    return {"message": "OK!", "items": items}
