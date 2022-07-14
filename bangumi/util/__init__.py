import os
from pathlib import Path

from dotenv import load_dotenv

from bangumi.consts.env import Env

from .files import move_file, get_relative_path
from .logger import setup_logger
from .torrent import extract_hash_from_url
from .decorator import safe_call


def init_folders():
    cache = Path(os.environ.get(Env.CACHE_FOLDER.value, "cache"))
    media = Path(os.environ.get(Env.MEDIA_FOLDER.value, "media"))
    media.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)


def setup_env():
    if os.path.exists(".env"):
        load_dotenv(".env")
