from dataclasses import dataclass, field
from typing import List


@dataclass
class RSSSite:
    url: str
    rules: List[str] = field(default_factory=lambda: [])

    # 文件大小如果小于该值，跳过。
    # 单位 bit
    min_size: int = 0

    def chop_url(self, size=32) -> str:
        ret = self.url[: size - 3] + ("..." if len(self.url) > (size - 3) else "")
        return ret.ljust(size)
