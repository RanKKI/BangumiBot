
from datetime import datetime
import os
from typing import List
from urllib.parse import urlparse

import bs4

from .rss_parser import RSSItem, RSSParser


class MiKanRSS(RSSParser):

    def is_matched(self, url: str) -> bool:
        return url.startswith("https://mikanani.me")

    def parse(self, content: bs4.BeautifulSoup) -> List[RSSItem]:
        ret = []

        for item in content.find_all("item"):
            title = item.find("title").text
            url = item.find("enclosure").get("url")
            pub_date = item.find("torrent").find("pubDate").text

            url_parts = urlparse(url)

            # 2022-07-06T23:00:52.205
            pub_datetime = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%S.%f")
            ret.append(RSSItem(
                title,
                url,
                int(pub_datetime.timestamp()),
                hash=os.path.splitext(os.path.basename(url_parts.path))[0]
            ))

        return ret
