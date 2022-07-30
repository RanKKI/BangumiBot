from bangumi.database import redisDB
from bangumi.downloader import downloader
from bangumi.shared import refresh_local

from .app import app as api


@api.get("/downloads")
async def get_downloads():
    return {"downloads": downloader.get_downloads()}


@api.get("/pending")
async def get_pending():
    return {"pending": redisDB.get_pending()}


@api.get("/refresh")
async def get_pending():
    refresh_local(redisDB, downloader)
    return {"message": "OK!"}
