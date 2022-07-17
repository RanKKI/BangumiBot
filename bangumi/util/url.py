from typing import Dict
from urllib.parse import urlencode, urlparse


def rebuild_url(url: str, extra: Dict[str, str]) -> str:
    parts = urlparse(url)
    extra_query = urlencode(extra)
    query = parts.query
    if query:
        query += "&" + extra_query
    else:
        query = extra_query
    return f"{parts.scheme}://{parts.netloc}{parts.path}?{query}"
