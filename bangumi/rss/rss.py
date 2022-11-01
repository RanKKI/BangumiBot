import logging
import os
import re
from collections import defaultdict
from pathlib import Path
from time import time
from typing import Dict, Iterable, List, Set, Union

from bangumi.entitiy import Configurable, RSSSite, WaitDownloadItem
from bangumi.parser import Parser
from bangumi.util import (
    dynamic_get_class,
    filter_download_item_by_rules,
    from_dict_to_dataclass,
    rebuild_url,
    first,
)
from tabulate import tabulate

from .dmhy import DMHYRSS
from .mikan import MiKanRSS
from .rss_parser import RSSParser

logger = logging.getLogger(__name__)


class RSS(Configurable):
    def __init__(self) -> None:
        self.__parsers: List[RSSParser] = [MiKanRSS(), DMHYRSS()]
        self.sites: List[RSSSite] = []
        self.rules = []  # 正则表达式，会过滤结果
        self.failed_hash: Set[str] = set()
        self.mapper: List[str] = []

    def reset_config(self):
        self.__parsers: List[RSSParser] = [MiKanRSS(), DMHYRSS()]
        self.sites: List[RSSSite] = []
        self.rules = []  # 正则表达式，会过滤结果
        self.failed_hash: Set[str] = set()
        self.mapper: List[str] = []

    def load_config(self, data) -> None:
        self.reset_config()
        self.mapper = data.get("mapper", [])

        for url in data.get("urls", []):
            site: RSSSite = None
            if isinstance(url, str):
                site = RSSSite(url=url)
            elif isinstance(url, dict):
                site = from_dict_to_dataclass(RSSSite, url)
            self.sites.append(site)

        self.rules = data.get("rules", [])

        for parser in data.get("parsers", []):
            self.__load_parser(parser)

        self.__validate_parser()
        self.__validate_mapper()

        self.log_config()

    def __load_parser(self, parser: Dict[str, Union[str, List[str]]]) -> None:
        folder = parser.get("folder", None)
        if not folder:
            return
        classes = parser.get("classes", [])
        logger.info(f"Loading parser plugin {folder} {classes}")
        if not os.path.exists(folder):
            logger.error(f"Failed to find parser plugin folder: {folder}")
            return
        clz_objects = dynamic_get_class(Path(folder), classes)
        self.__parsers.extend([clz() for clz in clz_objects])

    def __validate_parser(self):
        sites = self.sites[:]
        for site in sites:
            matched = False
            for parser in self.__parsers:
                if parser.is_matched(site.url):
                    matched = True
                    break
            if not matched:
                logger.error(f"Failed to match url: {site.url}")
                self.sites.remove(site)
                continue
            # get url domain
            logger.info(f"Matched url: {site.chop_url(35)} {str(parser)}")

    def __validate_mapper(self):
        mapper = self.mapper[:]
        for item in mapper:
            invalid = not isinstance(item, Iterable)
            invalid = invalid or len(item) != 2
            if invalid:
                logger.error(f"Invalid title mapper: {item}")
                self.mapper.remove(item)

    def get_parser(self, url: str) -> RSSParser:
        for parser in self.__parsers:
            if parser.is_matched(url):
                return parser
        return None

    async def scrape_url(
        self, site: RSSSite, last_scrape_time: int = 0
    ) -> List[WaitDownloadItem]:
        # 增加时间戳，避免缓存
        url = rebuild_url(site.url, {"_t": int(time())})
        logger.debug(f"Scraping url {url}")
        items = []
        parser = self.get_parser(url)
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
        items = self.map_title(items)
        # items = self.filter_by_time(items, last_scrape_time)
        items = filter_download_item_by_rules(self.rules, items)
        items = filter_download_item_by_rules(site.rules, items)
        items = self.filter_by_duplicate(items)
        return items

    async def scrape(self, last_scrape_time: int) -> List[WaitDownloadItem]:
        """
        在主循环中调用此方法，获取 RSS 数据
        """
        items = []

        for site in self.sites:
            items += await self.scrape_url(site, last_scrape_time=last_scrape_time)

        # items = self.filter_by_time(items, last_scrape_time)
        items = self.filter_by_duplicate(items)
        return items

    def map_title(self, items: List[WaitDownloadItem]) -> List[WaitDownloadItem]:
        def map_title(item: WaitDownloadItem) -> WaitDownloadItem:
            for *matcher, result in self.mapper:
                name = re.sub("\s+", " ", item.name)
                data = first(matcher, lambda x: re.match(x, name))
                if not data:
                    continue
                try:
                    item.name = result.format(*data.groups())
                    logger.debug(f"Mapped title from {name} to {item.name}")
                except Exception as e:
                    logger.error(f"Failed to format name {item.name} {data} {e}")
                break
            return item

        return list(map(map_title, items))

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
            if item.hash in self.failed_hash:
                continue
            try:
                info = Parser.parse_bangumi_name(item.name)
                seen[info.formatted].append((item, info.dpi))
            except ValueError:
                logger.error(f"Failed to parse bangumi name: {item.name}")
                self.failed_hash.add(item.hash)

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

    def log_config(self):
        table = []
        for i, rule in enumerate(self.rules):
            if i == 0:
                table.append(["*", rule])
            else:
                table.append(["", rule])
        for site in self.sites:
            if not site.rules:
                table.append([site.chop_url(35), ""])
                continue
            for i, rule in enumerate(site.rules):
                if i == 0:
                    table.append([site.chop_url(35), rule])
                else:
                    table.append(["", rule])
        string = tabulate(table, headers=["RSS Site", "Rules"], tablefmt="simple")
        for line in string.splitlines():
            logger.info(line)
        logger.info("")

        if self.mapper:
            logger.info("RSS Mapper:")
        for a, b in self.mapper:
            logger.info(f"┌ {a}")
            logger.info(f"└ {b}")
        if self.mapper:
            logger.info("")
