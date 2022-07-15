import json
import os
import unittest

from bangumi.manager import Notification


class TestRawParser(unittest.TestCase):
    def setUp(self) -> None:
        os.environ.setdefault("TEST_ENV", "1")
        return super().setUp()

    def test_http_call(self):
        ret = Notification().call_http(
            "https://httpbin.org/post",
            "this is a title",
            **{"method": "POST", "data": {"body": "12321321"}},
        )
        data = json.loads(ret)
        data = json.loads(data.get("data", "{}"))

        self.assertEqual(data.get("body"), "12321321")
        self.assertEqual(data.get("title"), "this is a title")

        ret = Notification().call_http(
            "https://httpbin.org/get?title={title}",
            "this is a title",
        )

        data = json.loads(ret)
        data = data.get("args", {})
        self.assertEqual(data.get("title"), "this is a title")

    def test_script_call(self):
        script_path = os.path.abspath("./test.sh")
        with open(script_path, "w") as f:
            f.write("echo $1")
        ret = Notification().call_script(f"/bin/sh {script_path}", "this is a title")
        self.assertEqual(ret.decode().strip(), "this is a title")
        os.remove(script_path)