import os
import re
from collections import defaultdict
from typing import List

from bangumi.parser import Parser
from loguru import logger

from .dmhy import DMHYRSS
from .mikan import MiKanRSS
from .rss_parser import RSSItem, RSSParser


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

    def scrape_url(self, url: str)-> List[RSSItem]:
        items = []
        for parser in self.__parsers:
            if parser.is_matched(url):
                content = parser.request_rss(url)
                if content is None:
                    logger.error(f"Failed to scrape {url}")
                else:
                    items = parser.parse(content)
        items = self.__filter_by_rules(items)
        items = self.filter_by_duplicate(items)
        items = self.filter_exists(items)
        return items

    def scrape(self, last_scrape_time: int) -> List[RSSItem]:
        """
        在主循环中调用此方法，获取 RSS 数据
        """
        items = []

        for url in self.urls:
            items += self.scrape_url(url)

        items = self.__filter_by_time(items, last_scrape_time)
        items = self.__filter_by_rules(items)
        items = self.filter_by_duplicate(items)
        items = self.filter_exists(items)

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
        """
        对重复的 RSS 数据进行过滤
        根据分辨率选择最高清的

        TODO: 语言优先级的处理
        """
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

    def filter_exists(self, items: List[RSSItem]) -> List[RSSItem]:
        """
        对已经存在（本地）的 RSS 数据进行过滤
        避免重复抓取
        """
        ret = []
        parser = Parser()
        for item in items:
            info = parser.analyse(item.name)
            path = info.get_full_path("")
            exists = False
            for file in path.parent.glob("*"):
                if not file.is_file():
                    continue
                file_name, _ = os.path.splitext(file.name)
                if file_name == path.name:
                    exists = True
                    break
            if not exists:
                ret.append(item)
        return ret
