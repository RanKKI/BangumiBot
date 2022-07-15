from typing import List

import bs4
from bangumi.entitiy import WaitDownloadItem
from bangumi.util import get_timestamp

from .rss_parser import RSSParser


class MiKanRSS(RSSParser):
    def is_matched(self, url: str) -> bool:
        return url.startswith("https://mikanani.me")

    def parse(self, content: bs4.BeautifulSoup) -> List[WaitDownloadItem]:
        ret = []
        for item in content.find_all("item"):
            title = item.find("title").text
            url = item.find("enclosure").get("url")
            pub_date = item.find("torrent").find("pubDate").text
            ret.append(
                WaitDownloadItem(
                    name=title,
                    url=url,
                    pub_at=get_timestamp(pub_date),
                )
            )
        return ret
