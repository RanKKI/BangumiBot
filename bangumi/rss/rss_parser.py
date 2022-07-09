import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

import bs4
import requests

logger = logging.getLogger(__name__)


@dataclass
class RSSItem:
    name: str
    url: str
    publish_at: int
    hash: str


class RSSParser(ABC):

    def request_rss(self, url: str) -> bs4.BeautifulSoup | None:
        ret = requests.get(url)
        if ret.status_code != 200:
            return None
        return bs4.BeautifulSoup(ret.text, "xml")

    @abstractmethod
    def is_matched(self, url: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def parse(self, content) -> List[RSSItem]:
        raise NotImplementedError()
