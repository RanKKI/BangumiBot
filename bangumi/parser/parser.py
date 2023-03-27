"""
该文件代码来自于 https://github.com/EstrellaXD/Auto_Bangumi/blob/c9c2b28389aac6ac4d778cdc7de1a77ca024b97e/auto_bangumi/Parser/analyser/raw_Parser.py

作者: EstrellaXD
协议: MIT
"""

import logging
import re
from typing import Union

from bangumi.entitiy import Episode
from bangumi.parser.ai_parse import AIParse
from functools import reduce
from bangumi.consts.env import Env

logger = logging.getLogger(__name__)

EPISODE_RE = re.compile(r"\d+")
TITLE_RE = re.compile(
    r"(.*|\[.*])( -? \d+ |\[\d+]|\[\d+.?[vV]\d{1}]|[第]\d+[话話集]|\[\d+.?END])(.*)"
)
RESOLUTION_RE = re.compile(r"1080|720|2160|4K")
SOURCE_RE = re.compile(r"B-Global|[Bb]aha|[Bb]ilibili|AT-X|Web")
SUB_RE = re.compile(r"[简繁日字幕]|CH|BIG5|GB")

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


class Parser:
    @staticmethod
    def get_group(name: str) -> str:
        return re.split(r"[\[\]]", name)[1]

    @staticmethod
    def pre_process(raw_name: str) -> str:
        return raw_name.replace("【", "[").replace("】", "]")

    @staticmethod
    def __season_process(season_info: str):
        if re.search(r"新番|月?番", season_info):
            name_season = re.sub(".*新番.", "", season_info)
        else:
            name_season = re.sub(r"^[^]】]*[]】]", "", season_info).strip()
        season_rule = r"S\d{1,2}|Season \d{1,2}|[第].[季期]"
        season_rule = r"S(\d{1,2}(?:\.5)?)|Season (\d{1,2}(?:\.5)?)|[第](.)[季期]"
        name_season = re.sub(r"[\[\]]", " ", name_season)
        seasons = re.findall(season_rule, name_season)
        if not seasons:
            return name_season, "", 1
        name = re.sub(season_rule, "", name_season)
        for season in filter(lambda x: x.strip(), reduce(lambda x, y: x + y, seasons)):
            season_raw = season
            try:
                if season.isnumeric():
                    season = int(season)
                else:
                    season = float(season)
            except ValueError:
                season = CHINESE_NUMBER_MAP.get(season, 1)
        return name, season_raw, season

    @staticmethod
    def __name_process(name: str):
        name = name.strip()
        split = re.split(r"/|\s{2}|-\s{2}", name.replace("（仅限港澳台地区）", ""))
        while "" in split:
            split.remove("")
        if len(split) == 1:
            if re.search("_{1}", name) is not None:
                split = re.split("_", name)
            elif re.search(" - {1}", name) is not None:
                split = re.split("-", name)
        if len(split) == 1:
            match_obj = re.match(r"([^\x00-\xff]{1,})(\s)([\x00-\xff]{4,})", name)
            if match_obj is not None:
                return match_obj.group(3), split
        compare, compare_idx = 0, 0
        for idx, name in list(enumerate(split)):
            l = re.findall("[aA-zZ]{1}", name).__len__()
            if l > compare:
                compare = l
                compare_idx = idx
        return split[compare_idx].strip(), split

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
        if not match_obj:
            raise ValueError("正则匹配失败")
        season_info, episode_info, other = list(
            map(lambda x: x.strip(), match_obj.groups())
        )
        raw_name, season_raw, season = Parser.__season_process(season_info)  # 处理 第n季
        name, name_group = "", ""
        try:
            name, name_group = Parser.__name_process(raw_name)  # 处理 名字
        except ValueError:
            pass
        # 处理 集数
        raw_episode = EPISODE_RE.search(episode_info)
        episode = 0
        if raw_episode is not None:
            episode = int(raw_episode.group())
        sub, dpi, source = Parser.find_tags(other)  # 剩余信息处理
        return name, season, season_raw, episode, sub, dpi, source, name_group, group

    @staticmethod
    def parse_bangumi_name(raw_title: str) -> Union[Episode, None]:
        """
        如果符合 XXXXXXXX S01E01 直接返回
        """
        if ret := re.match(r"(.*)S(\d{1,2})E(\d{1,2})", raw_title):
            epi = Episode()
            epi.title = ret.group(1)
            info.season_info.number, info.season_info.raw = int(
                ret.group(2)
            ), ret.group(2)
            epi.ep_info.number = int(ret.group(3))
            return epi

        open_ai_key = Env.get(Env.OPENAI_API_KEY, "", type=str)
        if open_ai_key:
            return AIParse.prase(raw_title)
        try:
            ret = Parser.__process(raw_title)
            if ret is None:
                return None
            name, season, sr, episode, sub, dpi, source, ng, group = ret
        except Exception as e:
            raise ValueError(f"解析失败 {e}")
        info = Episode()
        info.title = name
        info.season_info.number, info.season_info.raw = season, sr
        info.ep_info.number = episode
        info.subtitle, info.dpi, info.source = sub, dpi, source
        info.title_info.group = ng
        info.group = group
        return info
