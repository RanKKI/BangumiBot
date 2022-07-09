import os
from pathlib import Path

from bangumi.util.const import Env


def move_file(file: Path, folder_name: str, new_file_name: str) -> None:
    media_folder = Path(os.environ.get(Env.MEDIA_FOLDER.value, "media"))
    download_folder = Path(os.environ.get(Env.DOWNLOAD_FOLDER.value, "downloads"))
    ext = os.path.splitext(file.name)[1]
    target_folder = media_folder / folder_name
    target_folder.mkdir(parents=True, exist_ok=True)
    target_file = target_folder / f"{new_file_name}{ext}"

    abs_download_file = download_folder / file.name

    abs_download_file.rename(target_file)
