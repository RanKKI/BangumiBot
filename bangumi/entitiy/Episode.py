from dataclasses import dataclass

@dataclass
class TitleInfo:
    def __init__(self) -> None:
        self.raw: str = None
        self.name: str = None
        self.official: str = None
        self.group: list = None

@dataclass
class SeasonInfo:
    def __init__(self) -> None:
        self.raw: str = None
        self.number: int = None

@dataclass
class EpisodeInfo:
    def __init__(self) -> None:
        self.raw: str = None
        self.number: int = None

@dataclass
class Episode:

    @property
    def title(self) -> str:
        return self.title_info.name

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
        return f"{self.title} S{self.season_info.number}E{self.ep_info.number}"
