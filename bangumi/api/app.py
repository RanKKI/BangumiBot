import logging

from bangumi.database import redisDB
from bangumi.downloader import downloader
from bangumi.util import setup_env
from bangumi.util.logger import setup_logger
from fastapi import FastAPI

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def startup():
    setup_env()
    setup_logger()
    redisDB.connect()
    downloader.connect()
