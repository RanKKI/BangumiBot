from typing import Union
import json
import openai

import logging

from bangumi.consts.env import Env
from bangumi.entitiy import Episode
from collections import defaultdict

SYSTEM_PROMPT = """
你需要将我的输入转换成 JSON 类型， title 为字符串， season 为整数， episode 为整数， dpi 为字符串， subtitle 为字符串， source 为字符串， group 为字符串。

title 优选考虑英文、日文罗马文。如果没有英文、日文罗马文，那么就考虑将中文翻译成英文.

例如 [ANi] NieRAutomata Ver11a - 尼尔：自动人形 Ver1.1a - 05 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4][839.6 MB] [复制磁连] [资源简介]  将会被转成
```
{
    "title": "NieRAutomata Ver11a",
    "Season": "1",
    "Episode": "5",
    "Resolution": "1080P",
    "Source": "WEB-DL",
    "Sub": "CHT",
    "Format": "MP4",
    "Size": "839.6 MB",
    "Group": "ANi",
}
```

[XKsub&LoliHouse] 蓝色监狱 / Blue Lock Season 2 [19][WebRip 1080p HEVC-10bit AAC][简繁日内封字幕] [563.04 MB] [复制磁连]
则会转换成
```
{

    "title": "Blue Lock",
    "Season": "2",
    "Episode": "19",
    "Resolution": "1080P",
    "Source": "WebRip",
    "Sub": "简繁日内封字幕",
    "Format": "MP4",
    "Size": "563.04 MB",
    "Group": "XKsub&LoliHouse",
}
```

[XKsub&LoliHouse] 蓝色监狱 Season 3 [1][WebRip 1080p HEVC-10bit AAC][简繁日内封字幕] [563.04 MB] [复制磁连]

```
{

    "title": "Blue Lock",
    "Season": "3",
    "Episode": "01",
    "Resolution": "1080P",
    "Source": "WebRip",
    "Sub": "简繁日内封字幕",
    "Format": "MP4",
    "Size": "563.04 MB",
    "Group": "XKsub&LoliHouse",
}
```

明白的话，请回复 “明白"

"""

logger = logging.getLogger(__name__)


class AIParse(object):

    # make http request to openai api
    @staticmethod
    def request(title: str) -> str:
        logger.debug("ai parse request %s", title)
        openai.api_key = Env.get(Env.OPENAI_API_KEY, type=str)

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": title},
            ],
        )

        ret = completion.choices[0].message.content
        logger.debug("ai response %s", ret)
        return ret

    @staticmethod
    def prase(title: str) -> Union[Episode, None]:
        ret = defaultdict(str)
        ret.update(json.loads(AIParse.request(title)))

        info = Episode()
        info.title = ret["title"]
        info.season_info.number, info.season_info.raw = ret["Season"], ret["Season"]
        info.ep_info.number = ret["Episode"]
        info.subtitle, info.dpi, info.source = (
            ret["Sub"],
            ret["Resolution"],
            ret["Source"],
        )
        info.title_info.group = ret["Group"]
        info.group = ret["Group"]
        return info


if __name__ == "__main__":
    ret = AIParse.prase(
        "[星空字幕组][关于我在无意间被隔壁的天使变成废柴这件事 / Otonarino-tenshisama][07][繁日双语][1080P][WEBrip][MP4]（急招校对、后期） [297.08 MB] [复制磁连]"
    )
