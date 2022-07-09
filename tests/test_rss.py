import unittest

from bangumi.rss import RSS, RSSItem


class TestRawParser(unittest.TestCase):

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