import re
from typing import List
from bangumi.entitiy import WaitDownloadItem


def filter_download_item_by_rules(
    rules: List[str], items: List[WaitDownloadItem]
) -> List[WaitDownloadItem]:
    ret = []
    for item in items:
        matched = False
        for rule in rules:
            if re.match(rule, item.name):
                matched = True
                break
        if not matched:
            ret.append(item)

    return ret
