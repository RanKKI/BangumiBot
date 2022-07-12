import unittest

from bangumi.rss import RSS
from bangumi.entitiy import WaitDownloadItem
from bangumi.util.files import setup_test_env

class TestRawParser(unittest.TestCase):

    def setUp(self) -> None:
        setup_test_env()
        return super().setUp()

    def test_order(self):
        rss = RSS()
        items = [
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][1080p][繁日双语][招募翻译] [539.4 MB]",
                url=""
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][720p][繁日双语][招募翻译] [539.4 MB]",
                url=""
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][1080x1920][繁日双语][招募翻译] [539.4 MB]",
                url=""
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][4K][繁日双语][招募翻译] [539.4 MB]",
                url=""
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[9][1080][繁日双语][招募翻译] [539.4 MB]",
                url=""
            )
        ]
        items = rss.filter_by_duplicate(items)
        self.assertEqual(len(items), 3)
        for item in items:
            self.assertIn(item.name, [
                "【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][1080p][繁日双语][招募翻译] [539.4 MB]",
                "【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][4K][繁日双语][招募翻译] [539.4 MB]",
                "【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[9][1080][繁日双语][招募翻译] [539.4 MB]"
            ])

    def test_filter_by_time(self):
        items = [
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][1080p][繁日双语][招募翻译] [539.4 MB]",
                url="",
                pub_at=10
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][720p][繁日双语][招募翻译] [539.4 MB]",
                url="",
                pub_at=15
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][1080x1920][繁日双语][招募翻译] [539.4 MB]",
                url="",
                pub_at=15
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][4K][繁日双语][招募翻译] [539.4 MB]",
                url="",
                pub_at=20
            ),
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[9][1080][繁日双语][招募翻译] [539.4 MB]",
                url="",
                pub_at=20
            )
        ]

        rss = RSS()
        self.assertEqual(len(rss.filter_by_time(items, 10)), 4)
        self.assertEqual(len(rss.filter_by_time(items, 15)), 2)
        self.assertEqual(len(rss.filter_by_time(items, 20)), 0)

    def test_filter_by_rules(self):
        items = [
            WaitDownloadItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][1080p][繁日双语][招募翻译] [539.4 MB]",
                url="",
                pub_at=10
            ),
            WaitDownloadItem(
                name="【幻樱字幕组】【4月新番】【古见同学有交流障碍症 第二季 Komi-san wa, Komyushou Desu. S02】【22】【GB_MP4】【1920X1080】",
                url="",
                pub_at=15
            ),
            WaitDownloadItem(
                name="[爱恋&漫猫字幕组][4月新番][间谍过家家][SPY × FAMILY][12][1080p][MP4][简中]",
                url="",
                pub_at=15
            )
        ]

        rss = RSS()
        rss.rules = [
            r"^【喵萌奶茶屋】",
        ]
        self.assertEqual(len(rss.filter_by_rules(items)), 2, "rules: %s" % rss.rules)

        rss.rules = [
            r"^【幻樱字幕组】|\[爱恋&漫猫字幕组\]",
        ]
        self.assertEqual(len(rss.filter_by_rules(items)), 1, "rules: %s" % rss.rules)

        rss.rules = [
            r".*夏日重现.*",
        ]
        self.assertEqual(len(rss.filter_by_rules(items)), 2, "rules: %s" % rss.rules)

        rss.rules = [
            r".*夏日重现.*",
            r".*间谍过家家.*"
        ]
        self.assertEqual(len(rss.filter_by_rules(items)), 1, "rules: %s" % rss.rules)


