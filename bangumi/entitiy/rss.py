from dataclasses import dataclass, field
from typing import List


@dataclass
class RSSSite:
    url: str
    rules: List[str] = field(default_factory=lambda: [])

    def chop_url(self, size = 32) -> str:
        ret = self.url[:size - 3] + ("..." if len(self.url) > (size - 3) else "")
        return ret.ljust(size)