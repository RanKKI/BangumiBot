from dataclasses import dataclass, field
from typing import List


@dataclass
class RSSSite:
    url: str
    rules: List[str] = field(default_factory=lambda: [])
