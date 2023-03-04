import os
from dataclasses import dataclass
from pathlib import Path
import re

from bangumi.consts.env import Env


@dataclass
class TitleInfo:
    def __init__(self) -> None:
        self.raw: str = None
        self.name: str = None
        self.official: str = None
        self.group: list = None


@dataclass
class SeasonInfo:
    raw: str = ""
    number: int = 0


@dataclass
class EpisodeInfo:
    raw: str = ""
    number: int = 0


@dataclass
class Episode:
    @property
    def title(self) -> str:
        # 删除特殊字符
        ret = re.sub('[/\\\\:\*"<>|\?：]', " ", self.title_info.name)
        # 删除多余空格
        ret = re.sub("\s+", " ", ret)
        return ret.strip()

    @title.setter
    def title(self, title: str):
        self.title_info.name = title

    def __init__(self) -> None:
        self.group: str = None
        self.title_info = TitleInfo()
        self.season_info = SeasonInfo()
        self.ep_info = EpisodeInfo()
        self.dpi: str = None
        self.subtitle: str = None
        self.source: str = None

    @property
    def formatted(self) -> str:
        season = self.season_info.number
        season = str(int(season)).zfill(2)
        ep = str(self.ep_info.number).zfill(2)
        return f"{self.title} S{season}E{ep}"

    def get_full_path(self, ext: str = "") -> Path:
        media = Env.get(Env.MEDIA_FOLDER, "media", type=Path)
        season = self.season_info.number
        season_folder = f"Season {int(season)}"
        if season % 1 == 0.5:
            season_folder += " Part 2"
        return media / Path(self.title) / season_folder / f"{self.formatted}{ext}"
