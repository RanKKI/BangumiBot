import os
from pathlib import Path
import shutil

from bangumi.entitiy.episode import Episode
from bangumi.consts.env import Env


def get_relative_path(path: Path) -> Path:
    """
    获取相对路径
    """
    download_folder = Env.get(Env.DOWNLOAD_FOLDER, "downloads", type=Path)
    return download_folder / path.name


def move_file(file: Path, result: Episode, *, seeding=False) -> None:
    ext = os.path.splitext(file.name)[1]
    target_file = result.get_full_path(ext=ext)
    target_file.parent.mkdir(parents=True, exist_ok=True)
    # most of cases, the download drive and the storage drive are different
    # so instead of creating link between two directory, copy the data to
    # the storage drive and keep the original file in order to seed.
    # NOTICE: this will cause the file size to be doubled.
    #         and it's important to set auto-remove when seeding ratio reached or
    #         no enough spaces
    if seeding:
        shutil.copy(file, target_file)
    else:
        shutil.move(file, target_file)


def setup_test_env() -> Path:
    """
    测试环境初始化
    """
    cache_path = Path("./.cache")
    shutil.rmtree(cache_path, ignore_errors=True)

    cache_path.mkdir(parents=True, exist_ok=True)

    (cache_path / "media").mkdir(parents=True, exist_ok=True)

    os.environ.update(
        {
            Env.MEDIA_FOLDER.value: "./.cache/media",
            Env.DOWNLOAD_FOLDER.value: "./.cache",
        }
    )

    return cache_path
