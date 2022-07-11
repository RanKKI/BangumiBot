import unittest

from bangumi.rss import RSS, RSSItem
from bangumi.parser import Parser
from bangumi.util.files import setup_test_env

class TestRawParser(unittest.TestCase):

    def setUp(self) -> None:
        setup_test_env()
        return super().setUp()

    def test_order(self):
        rss = RSS(urls=[])
        items = [
            RSSItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][1080p][繁日双语][招募翻译] [539.4 MB]",
                url="",
                publish_at=0,
                hash=""
            ),
            RSSItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][720p][繁日双语][招募翻译] [539.4 MB]",
                url="",
                publish_at=0,
                hash=""
            ),
            RSSItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][1080x1920][繁日双语][招募翻译] [539.4 MB]",
                url="",
                publish_at=0,
                hash=""
            ),
            RSSItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][4K][繁日双语][招募翻译] [539.4 MB]",
                url="",
                publish_at=0,
                hash=""
            )
            ,
            RSSItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[9][1080][繁日双语][招募翻译] [539.4 MB]",
                url="",
                publish_at=0,
                hash=""
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

    def test_exists(self):
        rss = RSS(urls=[])
        item = RSSItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][1080p][繁日双语][招募翻译] [539.4 MB]",
                url="",
                publish_at=0,
                hash=""
            )
        parser = Parser()
        epi = parser.analyse(item.name)

        path = epi.get_full_path(".mp4")

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            f.write("test")

        self.assertTrue(path.exists())

        items = rss.filter_exists([
            item,
            RSSItem(
                name="【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][1080p][繁日双语][招募翻译] [539.4 MB]",
                url="",
                publish_at=0,
                hash=""
            )
        ])

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, "【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[10][1080p][繁日双语][招募翻译] [539.4 MB]")