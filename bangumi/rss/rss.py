import inspect
import json
import logging
import os
from pathlib import Path
import re
from collections import defaultdict
from typing import Dict, List, Union

from bangumi.entitiy.wait_download_item import WaitDownloadItem
from bangumi.parser import Parser
from bangumi.util.data_class import from_dict_to_dataclass
from bangumi.util.plugin import dynamic_get_class

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
        for rule in self.rules:
            logger.info(f"Loaded rule: {rule}")
        for parser in data.get("parsers", []):
            self.__load_parser(parser)

        self.__validate_parser()

    def __load_parser(self, parser: Dict[str, Union[str, List[str]]]) -> None:
        folder = parser.get("folder", None)
        if not folder:
            return
        classes = parser.get("classes", [])
        logger.info(f"Loading parser plugin {folder} {classes}")
        clz_objects = dynamic_get_class(Path(folder), classes)
        self.__parsers.extend([clz() for clz in clz_objects])

    def __validate_parser(self):
        for url in self.urls:
            matched = False
            for parser in self.__parsers:
                if parser.is_matched(url):
                    matched = True
                    break
            if not matched:
                logger.error(f"Failed to match url: {url}")
                self.urls.remove(url)
                continue
            # get url domain
            logger.info(f"Matched url: {url[:32]}... {inspect.getfile(parser.__class__)}")

    def __get_parser(self, url: str) -> RSSParser:
        for parser in self.__parsers:
            if parser.is_matched(url):
                return parser
        return None

    def scrape_url(self, url: str)-> List[WaitDownloadItem]:
        items = []
        parser = self.__get_parser(url)
        if not parser:
            logger.error(f"Failed to get parser for url: {url}")
            return []
        try:
            content = parser.request_rss(url)
        except Exception as e:
            logger.error(f"Failed to scrape {url} {e}")
            return []
        items = parser.parse(content)
        if not items:
            return []
        if not isinstance(items[0], WaitDownloadItem):
            items = [from_dict_to_dataclass(WaitDownloadItem, data) for data in items]
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