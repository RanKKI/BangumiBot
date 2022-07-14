from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class DownloadItem:
    hash: str
    name: str
    files: List[Path]
