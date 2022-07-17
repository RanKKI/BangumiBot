import inspect
import json
import logging
import os
import re
from collections import defaultdict
from pathlib import Path
from time import time
from typing import Dict, List, Union

from bangumi.entitiy import RSSSite, WaitDownloadItem
from bangumi.parser import Parser
from bangumi.util import (
    filter_download_item_by_rules,
    dynamic_get_class,
    from_dict_to_dataclass,
    rebuild_url,
)

from .dmhy import DMHYRSS
from .mikan import MiKanRSS
from .rss_parser import RSSParser

logger = logging.getLogger(__name__)


class RSS(object):
    def __init__(self) -> None:
        self.__parsers: List[RSSParser] = [MiKanRSS(), DMHYRSS()]
        self.sites: List[RSSSite] = []
        self.rules = [
            # 正则表达式，会过滤结果
        ]

    def load_config(self, config_path: str) -> None:
        if not os.path.exists(config_path):
            return
        with open(config_path, "r") as f:
            data = json.load(f)
        for url in data.get("urls", []):
            site: RSSSite = None
            if isinstance(url, str):
                site = RSSSite(url=url)
            elif isinstance(url, dict):
                site = from_dict_to_dataclass(RSSSite, url)
            self.sites.append(site)

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
        for site in self.sites:
            matched = False
            for parser in self.__parsers:
                if parser.is_matched(site.url):
                    matched = True
                    break
            if not matched:
                logger.error(f"Failed to match url: {site.url}")
                self.sites.remove(site.url)
                continue
            # get url domain
            logger.info(
                f"Matched url: {site.url[:32]}... {inspect.getfile(parser.__class__)}"
            )

    def __get_parser(self, url: str) -> RSSParser:
        for parser in self.__parsers:
            if parser.is_matched(url):
                return parser
        return None

    async def scrape_url(self, url: str) -> List[WaitDownloadItem]:
        # 增加时间戳，避免缓存
        url = rebuild_url(url, {"_t": int(time())})
        logger.debug(f"scraping url {url}")
        items = []
        parser = self.__get_parser(url)
        if not parser:
            logger.error(f"Failed to get parser for url: {url}")
            return []
        try:
            content = await parser.request_rss(url)
        except Exception as e:
            logger.error(f"Failed to scrape {url} {e}")
            return []
        items = parser.parse(content)
        if not items:
            return []
        if isinstance(items[0], dict):
            items = [from_dict_to_dataclass(WaitDownloadItem, data) for data in items]
        items = self.filter_by_duplicate(items)
        return items

    async def scrape(self, last_scrape_time: int) -> List[WaitDownloadItem]:
        """
        在主循环中调用此方法，获取 RSS 数据
        """
        items = []

        for site in self.sites:
            ret = await self.scrape_url(site.url)
            items += filter_download_item_by_rules(site.rules, ret)

        items = self.filter_by_time(items, last_scrape_time)
        items = filter_download_item_by_rules(self.rules, items)
        items = self.filter_by_duplicate(items)
        return items

    def filter_by_time(
        self, items: List[WaitDownloadItem], last_scrape_time: int
    ) -> List[WaitDownloadItem]:
        return [item for item in items if item.pub_at > last_scrape_time]

    def filter_by_duplicate(
        self, items: List[WaitDownloadItem]
    ) -> List[WaitDownloadItem]:
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
            val = sorted(val, key=lambda x: get_dpi_idx(x[1]))
            ret.append(val[0][0])

        return ret
