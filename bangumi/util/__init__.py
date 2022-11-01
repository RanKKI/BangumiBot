import os
from pathlib import Path
from typing import Any, Callable, Tuple

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
    cache = Env.get(Env.CACHE_FOLDER, "cache", type=Path)
    media = Env.get(Env.MEDIA_FOLDER, "media", type=Path)
    media.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)


def setup_env():
    if os.path.exists(".env"):
        load_dotenv(".env")


def first(arr: list, f: Callable[[Any], Tuple[None, Any]]) -> Any:
    for item in arr:
        ret = f(item)
        if ret:
            return ret
    return None