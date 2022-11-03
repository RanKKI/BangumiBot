from dataclasses import dataclass
import os
import re
from urllib.parse import urlparse


@dataclass
class WaitDownloadItem:
    name: str
    url: str
    pub_at: int = 0
    content_length: int = 0

    @property
    def hash(self):
        if self.url.startswith("magnet:"):
            return re.search(r"btih:([a-zA-Z0-9]{32})", self.url).group(1)
        if self.url.startswith("http"):
            return os.path.splitext(os.path.basename(urlparse(self.url).path))[0]
        raise ValueError("Invalid url: {}".format(self.url))
