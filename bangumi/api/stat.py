from .app import app as api
from bangumi.downloader import downloader
from bangumi.database import redisDB


@api.get("/downloads")
async def get_downloads():
    return {"downloads": downloader.get_downloads()}


@api.get("/pending")
async def get_pending():
    return {"pending": redisDB.get_pending()}
