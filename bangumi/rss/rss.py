from collections import defaultdict
import re
from time import time
from typing import List

from loguru import logger

from .dmhy import DMHYRSS
from .mikan import MiKanRSS
from .rss_parser import RSSItem, RSSParser
from bangumi.parser import Parser


class RSS(object):

    def __init__(self, urls: List[str]) -> None:
        self.__parsers: List[RSSParser] = [
            MiKanRSS(),
            DMHYRSS()
        ]
        self.urls = urls
        self.__rules = [
            # 正则表达式，会过滤结果
        ]

    def scrape(self, last_scrape_time: int) -> List[RSSItem]:
        """
        在主循环中调用此方法，获取 RSS 数据
        """
        items = []

        for url in self.urls:
            for parser in self.__parsers:
                if parser.is_matched(url):
                    content = parser.request_rss(url)
                    if content is None:
                        logger.error(f"Failed to scrape {url}")
                    else:
                        items += parser.parse(content)
                    break

        items = self.__filter_by_time(items, last_scrape_time)
        items = self.__filter_by_rules(items)
        items = self.filter_by_duplicate(items)

        return items

    def __filter_by_time(self, items: List[RSSItem], last_scrape_time: int) -> List[RSSItem]:
        return [item for item in items if item.publish_at > last_scrape_time]

    def __filter_by_rules(self, items: List[RSSItem]) -> List[RSSItem]:
        ret = []

        for item in items:
            matched = False
            for rule in self.__rules:
                if re.match(rule, item.name):
                    matched = True
                    break
            if not matched:
                ret.append(item)

        return ret

    def filter_by_duplicate(self, items: List[RSSItem]) -> List[RSSItem]:
        ret = []
        parser = Parser()
        seen = defaultdict(lambda: [])

        for item in items:
            info = parser.analyse(item.name)
            seen[info.formatted].append((item, info.dpi))

        dpi_arr = "720|1080|2160|4K".split("|")

        def get_dpi_idx(dpi: str) -> int:
            if not dpi:
                return 0
            for i, d in enumerate(dpi_arr):
                if re.search(str(d), dpi):
                    return -i
            return 10000

        for val in seen.values():
            # sort val by dpi
            val = sorted(val, key=lambda x:get_dpi_idx(x[1]))
            ret.append(val[0][0])

        return ret
