import time

from cache import TTLCache


def test_entry_is_returned_before_ttl():
    cache = TTLCache(ttl=10)
    cache.set("k", 1)
    assert cache.get("k") == 1


def test_entry_expires_after_ttl():
    cache = TTLCache(ttl=0.05)
    cache.set("k", 1)
    time.sleep(0.05)
    assert cache.get("k") is None
