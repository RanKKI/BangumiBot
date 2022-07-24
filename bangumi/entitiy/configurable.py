from abc import ABC
from typing import Any, Dict


class Configurable(ABC):
    def load_config(self, data: Dict[str, Any]):
        pass
