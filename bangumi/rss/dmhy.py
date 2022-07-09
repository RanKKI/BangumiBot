
from datetime import datetime
from typing import List

import bs4
import re

from .rss_parser import RSSItem, RSSParser
from urllib.parse import urlparse

class DMHYRSS(RSSParser):

    def is_matched(self, url: str) -> bool:
        return url.startswith("https://dmhy.org")

    def parse(self, content: bs4.BeautifulSoup) -> List[RSSItem]:
        ret = []

        for item in content.find_all("item"):
            title = item.find("title").text
            url = item.find("enclosure").get("url")
            url_parts = urlparse(url)
            pub_date = item.find("pubDate").text
            pub_datetime = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
            ret.append(RSSItem(
                title,
                url,
                int(pub_datetime.timestamp()),
                hash=re.search("[a-zA-Z0-9]{32}", url_parts.query).group()
            ))

        return ret
