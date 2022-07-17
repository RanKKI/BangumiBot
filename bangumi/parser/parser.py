"""
该文件代码来自于 https://github.com/EstrellaXD/Auto_Bangumi/blob/c9c2b28389aac6ac4d778cdc7de1a77ca024b97e/auto_bangumi/Parser/analyser/raw_Parser.py

作者: EstrellaXD
协议: MIT
"""

from functools import reduce
import logging
import re
from typing import List, Union

from bangumi.entitiy import Episode

logger = logging.getLogger(__name__)

EPISODE_RE = re.compile(r"\d+")
TITLE_RE = re.compile(
    r"(.*|\[.*])( -? \d+ |\[\d+]|\[\d+.?[vV]\d{1}]|[第]\d+[话話集]|\[\d+.?END])(.*)"
)
RESOLUTION_RE = re.compile(r"1080|720|2160|4K")
SOURCE_RE = re.compile(r"B-Global|[Bb]aha|[Bb]ilibili|AT-X|Web")
SUB_RE = re.compile(r"字幕|CH|BIG5|GB|简体|繁體|繁体|简")

CHINESE_NUMBER_MAP = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}


def is_valid_parentheses(s: str) -> bool:
    """
    判断字符串是否是合法的括号
    """
    stack = []
    for c in s:
        if c == "(":
            stack.append(c)
        elif c == ")":
            if len(stack) == 0:
                return False
            stack.pop()
    return len(stack) == 0


class Parser:
    @staticmethod
    def get_group(name: str) -> str:
        return re.split(r"[\[\]]", name)[1]

    @staticmethod
    def pre_process(raw_name: str) -> str:
        return (
            raw_name.replace("【", "[")
            .replace("】", "]")
            .replace("（", "(")
            .replace("）", ")")
        )

    @staticmethod
    def __season_process(season_info: str):
        if re.search(r"新番|月?番", season_info):
            name_season = re.sub(".*新番.", "", season_info)
        else:
            name_season = re.sub(r"^[^]】]*[]】]", "", season_info).strip()
        season_rule = r"S\d{1,2}|Season \d{1,2}|[第].[季期]"
        name_season = re.sub(r"[\[\]]", " ", name_season)
        seasons = re.findall(season_rule, name_season)
        if not seasons:
            return name_season, "", 1
        name = re.sub(season_rule, "", name_season)
        for season in seasons:
            season_raw = season
            if re.search(r"S|Season", season) is not None:
                season = int(re.sub(r"S|Season", "", season))
                break
            elif re.search(r"[第 ].*[季期]", season) is not None:
                season_pro = re.sub(r"[第季期 ]", "", season)
                try:
                    season = int(season_pro)
                except ValueError:
                    season = CHINESE_NUMBER_MAP[season_pro]
                    break
        return name, season_raw, season

    @staticmethod
    def __name_process(name: str):
        name = name.strip().replace("  ", " ")
        name = re.sub(r"\({0,1}(仅|僅)限港澳台地(区|區)\){0,1}", "", name)
        # remove year in the end
        name = re.sub(r"(\d{4}\s*)*$", "", name)

        # 删除日期
        name = re.sub(r"\d{4}年\d{1,2}月", "", name)

        """
        "[动漫萌][4月新番][Spy  X Family ][BIG5][06][1080P](字幕组招募内详)"
        针对当字幕出现在集数之前的情况，
        字幕信息会被认为是标题信息
        因此删除
        """
        for sub in SUB_RE.findall(name):
            name = name.replace(sub, "")

        NON_CJK = "[^\u4e00-\u9fa5\u30a0-\u30ff\u3040-\u309f]"

        possible_names = set()
        patterns = ["( - )", "/"]
        for pattern in patterns:
            for result in re.split(pattern, name):
                if not result:
                    continue
                possible_names.add(result)

            sub_result = [re.split(pattern, name or "") for name in possible_names]
            for result in reduce(lambda x, y: x + y, sub_result, []):
                if not result:
                    continue
                possible_names.add(result)

        possible_names = list(filter(lambda x: x, possible_names))

        split_names = list(filter(lambda x: x != name, possible_names))

        possible_names = [
            re.findall(rf"[^\w]*({NON_CJK}+)[^\w]*", name) for name in possible_names
        ]

        possible_names = reduce(lambda x, y: x + y, possible_names, [])
        possible_names = map(lambda x: x.strip(), possible_names)

        """
        拍脑子定的, 最长的名字必须大于 3 个字符，
        [ANi]  神渣☆偶像 - 01 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]
        格式化出来是 ['☆'] 因此需要过滤
        """
        possible_names = filter(lambda x: len(x) > 3, possible_names)
        possible_names = list(possible_names)

        def key(x: str):
            rank = len(x)
            if not "-" in x and not "/" in x:
                return rank
            if "-" in x:
                return rank - 10
            if "/" in x:
                return rank - 15
            return rank

        possible_names.sort(key=key, reverse=True)

        ret = None

        if possible_names:
            ret = possible_names[0]
        elif split_names:
            ret = max(split_names, key=len)

        if ret:
            if ret.count("_") == 1:
                ret = max(ret.split("_"), key=len)
            if not is_valid_parentheses(ret):
                ret = ret.strip("()")
            ret = ret.strip("-\\.,[] _/\u200b")
        return ret or name.strip()

    @staticmethod
    def find_tags(other):
        elements = re.sub(r"[\[\]()（）]", " ", other).split(" ")
        # find CHT
        sub, resolution, source = None, None, None
        for element in filter(lambda x: x != "", elements):
            if SUB_RE.search(element):
                sub = element
            elif RESOLUTION_RE.search(element):
                resolution = element
            elif SOURCE_RE.search(element):
                source = element
        return Parser.__clean_sub(sub), resolution, source

    @staticmethod
    def __clean_sub(sub: str) -> str:
        if sub is None:
            return sub
        # TODO: 这里需要改成更精准的匹配，可能不止 _MP4 ?
        return re.sub(r"_MP4|_MKV", "", sub)

    @staticmethod
    def __process(raw_title: str):
        raw_title = raw_title.strip()
        content_title = Parser.pre_process(raw_title)  # 预处理标题
        group = Parser.get_group(content_title)  # 翻译组的名字
        match_obj = TITLE_RE.match(content_title)  # 处理标题
        season_info, episode_info, other = list(
            map(lambda x: x.strip(), match_obj.groups())
        )
        raw_name, season_raw, season = Parser.__season_process(season_info)  # 处理 第n季
        name = ""
        try:
            name = Parser.__name_process(raw_name)  # 处理 名字
        except ValueError:
            pass
        # 处理 集数
        raw_episode = EPISODE_RE.search(episode_info)
        episode = 0
        if raw_episode is not None:
            episode = int(raw_episode.group())
        sub, dpi, source = Parser.find_tags(other)  # 剩余信息处理
        return name, season, season_raw, episode, sub, dpi, source, group

    @staticmethod
    def parse_bangumi_name(raw_title: str) -> Union[Episode, None]:
        try:
            ret = Parser.__process(raw_title)
            if ret is None:
                return None
            name, season, sr, episode, sub, dpi, source, group = ret
        except Exception as e:
            logger.error(f"ERROR match {raw_title} {e}")
            return None
        info = Episode()
        info.title = name
        info.season_info.number, info.season_info.raw = season, sr
        info.ep_info.number = episode
        info.subtitle, info.dpi, info.source = sub, dpi, source
        info.group = group
        return info
