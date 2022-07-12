
from datetime import datetime
from typing import List

import bs4
from bangumi.entitiy import WaitDownloadItem

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
            # 2022-07-06T23:00:52.205
            pub_datetime = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%S.%f")
            ret.append(WaitDownloadItem(
                name=title,
                url=url,
                pub_at=int(pub_datetime.timestamp()),
            ))

        return ret
