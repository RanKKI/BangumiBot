import re
from time import time
from typing import List

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
        self.__last_scrape_time = 0
        self.__rules = [
            # 正则表达式，会过滤结果
        ]

    def scrape(self) -> List[RSSItem]:
        """
        在主循环中调用此方法，获取 RSS 数据
        """
        items = []

        for url in self.urls:
            for parser in self.__parsers:
                if parser.is_matched(url):
                    content = parser.request_rss(url)
                    items += parser.parse(content)
                    break

        items = self.__filter_by_time(items)
        items = self.__filter_by_rules(items)
        self.__update_last_scrape_time()

        return items

    def __update_last_scrape_time(self) -> None:
        self.__last_scrape_time = int(time())

    def __filter_by_time(self, items: List[RSSItem]) -> List[RSSItem]:
        return [item for item in items if item.publish_at > self.__last_scrape_time]

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

