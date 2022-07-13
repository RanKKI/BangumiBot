import unittest

from bangumi.database import redisDB


class TestRawParser(unittest.TestCase):

    def test_redis_key(self):
        f = redisDB.get_key_from_formatted_name
        self.assertEqual(f("test S02E01"), "test:S02E01")
        self.assertEqual(f("测试 一二 啊 S02E01"), "测试_一二_啊:S02E01")
        self.assertEqual(f("测试 一二 啊  S02E01"), "测试_一二_啊:S02E01")
