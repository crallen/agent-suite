import time
import unittest

from cache import TTLCache


class TTLCacheTest(unittest.TestCase):
    def test_entry_is_returned_before_ttl(self):
        cache = TTLCache(ttl=10)
        cache.set("k", 1)
        self.assertEqual(cache.get("k"), 1)

    def test_entry_expires_after_ttl(self):
        cache = TTLCache(ttl=0.05)
        cache.set("k", 1)
        time.sleep(0.06)
        self.assertIsNone(cache.get("k"))

    def test_entry_without_ttl_never_expires(self):
        cache = TTLCache(ttl=None)
        cache.set("k", 1)
        time.sleep(0.01)
        self.assertEqual(cache.get("k"), 1)


if __name__ == "__main__":
    unittest.main()
