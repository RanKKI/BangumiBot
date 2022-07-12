import json
import logging
import os
import re
from collections import defaultdict
from typing import List

from bangumi.entitiy.wait_download_item import WaitDownloadItem
from bangumi.parser import Parser

from .dmhy import DMHYRSS
from .mikan import MiKanRSS
from .rss_parser import RSSParser

logger = logging.getLogger(__name__)

class RSS(object):

    def __init__(self, urls: List[str] = None) -> None:
        self.__parsers: List[RSSParser] = [
            MiKanRSS(),
            DMHYRSS()
        ]
        self.urls = urls or []
        self.rules = [
            # 正则表达式，会过滤结果
        ]

    def load_config(self, config_path: str) -> None:
        if not os.path.exists(config_path):
            return
        with open(config_path, "r") as f:
            data = json.load(f)
        self.urls = data.get("urls", [])
        self.rules = data.get("rules", [])
        for url in self.urls:
            logger.info(f"Loaded url: {url}")
        for rule in self.rules:
            logger.info(f"Loaded rule: {rule}")

    def scrape_url(self, url: str)-> List[WaitDownloadItem]:
        items = []
        for parser in self.__parsers:
            if parser.is_matched(url):
                content = parser.request_rss(url)
                if content is None:
                    logger.error(f"Failed to scrape {url}")
                else:
                    items = parser.parse(content)
        items = self.filter_by_rules(items)
        items = self.filter_by_duplicate(items)
        return items

    def scrape(self, last_scrape_time: int) -> List[WaitDownloadItem]:
        """
        在主循环中调用此方法，获取 RSS 数据
        """
        items = []

        for url in self.urls:
            items += self.scrape_url(url)

        items = self.filter_by_time(items, last_scrape_time)
        items = self.filter_by_rules(items)
        items = self.filter_by_duplicate(items)
        return items

    def filter_by_time(self, items: List[WaitDownloadItem], last_scrape_time: int) -> List[WaitDownloadItem]:
        return [item for item in items if item.pub_at > last_scrape_time]

    def filter_by_rules(self, items: List[WaitDownloadItem]) -> List[WaitDownloadItem]:
        ret = []

        for item in items:
            matched = False
            for rule in self.rules:
                if re.match(rule, item.name):
                    matched = True
                    break
            if not matched:
                ret.append(item)

        return ret

    def filter_by_duplicate(self, items: List[WaitDownloadItem]) -> List[WaitDownloadItem]:
        """
        对重复的 RSS 数据进行过滤
        根据分辨率选择最高清的

        TODO: 语言优先级的处理
        """
        ret = []
        seen = defaultdict(lambda: [])

        for item in items:
            info = Parser.parse_bangumi_name(item.name)
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