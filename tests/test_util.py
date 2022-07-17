import unittest

from bangumi.util import rebuild_url


class TestRawParser(unittest.TestCase):
    def test_rebuild_url(self):
        url = "https://www.example.org/rss?token=123"
        url = rebuild_url(url, {"_t": "456"})
        self.assertEqual(url, "https://www.example.org/rss?token=123&_t=456")
