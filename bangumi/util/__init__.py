import os
from pathlib import Path

from .const import Env
from .logger import setup_logger
from .files import move_file


def init_folders():
    Path(os.environ.get(Env.CACHE_FOLDER.value, "cache")).mkdir(parents=True, exist_ok=True)
    Path(os.environ.get(Env.MEDIA_FOLDER.value, "media")).mkdir(parents=True, exist_ok=True)
