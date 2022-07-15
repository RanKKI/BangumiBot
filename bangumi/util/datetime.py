
from datetime import datetime


POSSIBLE_FORMAT = [
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",
    "%a, %d %b %Y %H:%M:%S %z"
]

def get_timestamp(val: str) -> int:
    for format in POSSIBLE_FORMAT:
        try:
            return int(datetime.strptime(val, format).timestamp())
        except ValueError:
            continue
    raise ValueError(f"Invalid timestamp {val}")