from dataclasses import dataclass

from bangumi.util.torrent import extract_hash_from_url


@dataclass
class WaitDownloadItem:
    name: str
    url: str
    pub_at: int = 0

    @property
    def hash(self):
        return extract_hash_from_url(self.url)
