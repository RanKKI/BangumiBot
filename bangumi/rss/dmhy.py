from datetime import datetime
from typing import List

import bs4

from bangumi.entitiy import WaitDownloadItem

from .rss_parser import RSSParser


class DMHYRSS(RSSParser):
    def is_matched(self, url: str) -> bool:
        return url.startswith("https://dmhy.org")

    def parse(self, content: bs4.BeautifulSoup) -> List[WaitDownloadItem]:
        ret = []
        for item in content.find_all("item"):
            title = item.find("title").text
            url = item.find("enclosure").get("url")
            pub_date = item.find("pubDate").text
            pub_datetime = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
            ret.append(
                WaitDownloadItem(
                    name=title,
                    url=url,
                    pub_at=int(pub_datetime.timestamp()),
                )
            )

        return ret
