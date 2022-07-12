
import os
import re
from urllib.parse import urlparse


def extract_hash_from_url(url: str) -> str:
    if url.startswith("magnet:"):
        return re.search(r"btih:([a-zA-Z0-9]{32})", url).group(1)
    if url.startswith("http"):
        return os.path.splitext(os.path.basename(urlparse(url).path))[0]
    raise ValueError("Invalid url: {}".format(url))