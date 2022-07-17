import os
from pathlib import Path

from dotenv import load_dotenv

from bangumi.consts.env import Env

from .files import move_file, get_relative_path, setup_test_env
from .logger import setup_logger
from .decorator import safe_call
from .rss import filter_download_item_by_rules
from .clz import from_dict_to_dataclass
from .plugin import dynamic_get_class
from .datetime import get_timestamp
from .url import rebuild_url


def init_folders():
    cache = Path(os.environ.get(Env.CACHE_FOLDER.value, "cache"))
    media = Path(os.environ.get(Env.MEDIA_FOLDER.value, "media"))
    media.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)


def setup_env():
    if os.path.exists(".env"):
        load_dotenv(".env")
