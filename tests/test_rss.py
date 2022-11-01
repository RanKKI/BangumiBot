import unittest

from fastapi import Path

from bangumi.rss import RSS
from bangumi.entitiy import WaitDownloadItem
from bangumi.util import setup_test_env, filter_download_item_by_rules


class TestRawParser(unittest.TestCase):
    def setUp(self) -> None:
        setup_test_env()
        return super().setUp()

    def test_config(self):
        RSS().load_config({})

    def test_order(self):
        rss = RSS()
        items = [
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][1080p][繁日双语][招募翻译] [539.4 MB]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][720p][繁日双语][招募翻译] [539.4 MB]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][1080x1920][繁日双语][招募翻译] [539.4 MB]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][4K][繁日双语][招募翻译] [539.4 MB]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[9][1080][繁日双语][招募翻译] [539.4 MB]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
            ),
        ]
        items = rss.filter_by_duplicate(items)
        self.assertEqual(len(items), 3)
        for item in items:
            self.assertIn(
                item.name,
                [
                    "【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][1080p][繁日双语][招募翻译] [539.4 MB]",
                    "【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][4K][繁日双语][招募翻译] [539.4 MB]",
                    "【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[9][1080][繁日双语][招募翻译] [539.4 MB]",
                ],
            )

    def test_filter_by_time(self):
        items = [
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][1080p][繁日双语][招募翻译] [539.4 MB]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=10,
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][720p][繁日双语][招募翻译] [539.4 MB]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=15,
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][1080x1920][繁日双语][招募翻译] [539.4 MB]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=15,
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][4K][繁日双语][招募翻译] [539.4 MB]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=20,
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[9][1080][繁日双语][招募翻译] [539.4 MB]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=20,
            ),
        ]

        rss = RSS()
        self.assertEqual(len(rss.filter_by_time(items, 10)), 4)
        self.assertEqual(len(rss.filter_by_time(items, 15)), 2)
        self.assertEqual(len(rss.filter_by_time(items, 20)), 0)

    def test_filter_by_rules(self):
        items = [
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][1080p][繁日双语][招募翻译] [539.4 MB]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=10,
            ),
            WaitDownloadItem(
                name="【幻樱字幕组】【4月新番】【古见同学有交流障碍症 第二季 Komi-san wa, Komyushou Desu. S02】【22】【GB_MP4】【1920X1080】",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=15,
            ),
            WaitDownloadItem(
                name="[爱恋&漫猫字幕组][4月新番][间谍过家家][SPY × FAMILY][12][1080p][MP4][简中]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=15,
            ),
        ]

        rule_cases = [
            (
                [
                    r"^【喵萌奶茶屋】",
                ],
                2,
            ),
            (
                [
                    r"^【幻樱字幕组】|\[爱恋&漫猫字幕组\]",
                ],
                1,
            ),
            (
                [
                    r".*夏日重现.*",
                ],
                2,
            ),
            ([r".*夏日重现.*", r".*间谍过家家.*"], 1),
        ]
        for rules, expected_count in rule_cases:
            output = filter_download_item_by_rules(rules=rules, items=items)
            self.assertEqual(len(output), expected_count, rules)

    def test_mapper(self):
        rss = RSS()
        rss.mapper = [
            [
                "^\[ANi\] 即使如此依旧步步进逼（仅限港澳台地区） - (\d+) (\[.*\]\s*)+",
                "Soredemo Ayumu wa Yosetekuru - {} {}",
            ]
        ]
        items = [
            WaitDownloadItem(
                name="[NaN-Raws]即使如此依旧步步进逼[3][Bilibili][WEB-DL][1080P][AVC_AAC][CHT][MP4][bangumi.online]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=10,
            ),
            WaitDownloadItem(
                name="[ANi] 即使如此依旧步步进逼（仅限港澳台地区） - 03 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=10,
            ),
        ]
        i = rss.map_title(items)
        self.assertEqual(
            i[0].name,
            "[NaN-Raws]即使如此依旧步步进逼[3][Bilibili][WEB-DL][1080P][AVC_AAC][CHT][MP4][bangumi.online]",
        )
        self.assertEqual(
            i[1].name,
            "Soredemo Ayumu wa Yosetekuru - 03 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]",
        )

        rss.mapper = [
            [
                "^\[ANi\] 即使如此依旧步步进逼（仅限港澳台地区） - (\d+) (\[.*\]\s*)+",
                "Soredemo Ayumu wa Yosetekuru - {} {}",
            ],
            [
                "^\[NaN-Raws\]即使如此依旧步步进逼\[(\d+)\](\[.*\]\s*)+",
                "Soredemo Ayumu wa Yosetekuru - {} {}",
            ],
        ]
        i = rss.map_title(items)
        self.assertEqual(
            i[0].name,
            "Soredemo Ayumu wa Yosetekuru - 3 [Bilibili][WEB-DL][1080P][AVC_AAC][CHT][MP4][bangumi.online]",
        )
        self.assertEqual(
            i[1].name,
            "Soredemo Ayumu wa Yosetekuru - 03 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]",
        )

    def test_multiple_mapper(self):
        rss = RSS()
        items = [
            WaitDownloadItem(
                name="[NaN-Raws]即使如此依旧步步进逼[3][Bilibili][WEB-DL][1080P][AVC_AAC][CHT][MP4][bangumi.online]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=10,
            ),
            WaitDownloadItem(
                name="[ANi] 即使如此依旧步步进逼（仅限港澳台地区） - 03 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=10,
            ),
            WaitDownloadItem(
                name="即使如此依旧步步进逼第4集[1080P]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=10,
            ),
        ]
        rss.mapper = [
            [
                "^\[ANi\] 即使如此依旧步步进逼（仅限港澳台地区） - (\d+) (\[.*\]\s*)+",
                "^\[NaN-Raws\]即使如此依旧步步进逼\[(\d+)\](\[.*\]\s*)+",
                "^即使如此依旧步步进逼第(\d+)集(\[.*\]\s*)+",
                "Soredemo Ayumu wa Yosetekuru - {} {}",
            ]
        ]
        i = rss.map_title(items)
        self.assertEqual(
            i[0].name,
            "Soredemo Ayumu wa Yosetekuru - 3 [Bilibili][WEB-DL][1080P][AVC_AAC][CHT][MP4][bangumi.online]",
        )
        self.assertEqual(
            i[1].name,
            "Soredemo Ayumu wa Yosetekuru - 03 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]",
        )
        self.assertEqual(
            i[2].name,
            "Soredemo Ayumu wa Yosetekuru - 4 [1080P]",
        )
