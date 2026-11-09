import time


class TTLCache:
    """A dict whose entries expire `ttl` seconds after they are set.

    With `ttl=None`, entries never expire.
    """

    def __init__(self, ttl):
        self.ttl = ttl
        self._data = {}

    def set(self, key, value):
        self._data[key] = (value, time.time())

    def get(self, key):
        value, stored_at = self._data.get(key, (None, 0.0))
        if self.ttl and time.time() - stored_at > self.ttl:
            return None
        return value
