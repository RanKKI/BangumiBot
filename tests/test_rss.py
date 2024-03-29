import unittest

from bangumi.entitiy import WaitDownloadItem
from bangumi.rss import RSS
from bangumi.rss.mikan import MiKanRSS
from bangumi.util import (
    filter_download_item_by_content_length,
    filter_download_item_by_rules,
    setup_test_env,
)
import bs4


class TestRawParser(unittest.TestCase):
    def setUp(self) -> None:
        setup_test_env()
        return super().setUp()

    def test_config(self):
        rss = RSS()
        rss.load_config(
            {
                "urls": [
                    {
                        "url": "https://dmhy.org/topics/rss/rss.xml",
                        "rules": [".*[^(來自深淵)|(来自深渊)].*", ".*21321*"],
                        "min_size": 18423,
                    },
                ],
            }
        )
        self.assertEqual(len(rss.sites), 1)
        self.assertEqual(rss.sites[0].url, "https://dmhy.org/topics/rss/rss.xml")
        self.assertEqual(rss.sites[0].min_size, 18423)

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

    def test_spaces_with_mapper(self):
        rss = RSS()
        items = [
            WaitDownloadItem(
                name="[桜都字幕组] 夫妇以上，恋人未满。/   Fuufu Ijou, Koibito Miman. [04][1080p][简繁内封]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=10,
            )
        ]
        rss.mapper = [
            [
                ".*夫妇以上，恋人未[满満]。/ Fuufu Ijou, Koibito Miman. \[(\d+)\]((\[.*\])*)",
                "[桜都字幕组] Fuufu Ijou, Koibito Miman 第{}集 {}",
            ]
        ]
        ret = rss.map_title(items)
        self.assertEqual(
            ret[0].name,
            "[桜都字幕组] Fuufu Ijou, Koibito Miman 第04集 [1080p][简繁内封]",
        )

    def test_min_content_length(self):
        items = [
            WaitDownloadItem(
                name="[桜都字幕组] 夫妇以上，恋人未满。/   Fuufu Ijou, Koibito Miman. [04][1080p][简繁内封]",
                url="https://mikanani.me/Download/20220719/6eaa5bb1584dbe437444bbd2b42e071ac88a50ed.torrent",
                pub_at=10,
                content_length=10 * 1024 * 1024,
            )
        ]
        items = filter_download_item_by_content_length(9 * 1024 * 1024, items)
        self.assertEqual(len(items), 1)

        items = filter_download_item_by_content_length(11 * 1024 * 1024, items)
        self.assertEqual(len(items), 0)

    def test_mikan_parser(self):
        mikan = MiKanRSS()
        root = bs4.BeautifulSoup(
            """<rss><channel><item><guid isPermaLink="false">[V2][织梦字幕组][电锯人 Chainsaw Man][04集][1080P][AVC][简日双语]</guid><link>https://mikanani.me/Home/Episode/2f0854887541481bbe747c113a1083bf2637ccd2</link><title>[V2][织梦字幕组][电锯人 Chainsaw Man][04集][1080P][AVC][简日双语]</title><description>[V2][织梦字幕组][电锯人 Chainsaw Man][04集][1080P][AVC][简日双语][421.56 MB]</description><torrent xmlns="https://mikanani.me/0.1/"><link>https://mikanani.me/Home/Episode/2f0854887541481bbe747c113a1083bf2637ccd2</link><contentLength>442037696</contentLength><pubDate>2022-11-03T08:10:43.331</pubDate></torrent><enclosure type="application/x-bittorrent" length="442037696" url="https://mikanani.me/Download/20221103/2f0854887541481bbe747c113a1083bf2637ccd2.torrent"/></item></channel></rss>""", features="xml"
        )
        items = mikan.parse(root)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, "[V2][织梦字幕组][电锯人 Chainsaw Man][04集][1080P][AVC][简日双语]")
        self.assertEqual(items[0].content_length, 442037696)
