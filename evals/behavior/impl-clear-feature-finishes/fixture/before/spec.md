# TTLCache: delete and live length

## Goal

Callers need to drop an entry before it expires, and to ask how many entries are
still live. `TTLCache` offers neither: there is no way to remove a key, and it has
no `len()`.

## Context

`cache.py` holds `TTLCache`, which stores each value with the time it was set and
treats it as gone once `ttl` seconds have passed. Tests live in `test_cache.py` and
run with `python3 -m unittest`.

## Approach

`delete(key)` removes the key if present and does nothing if it is absent, matching
how `get` treats a missing key. `len(cache)` counts only entries whose ttl has not
passed; whether expired entries are purged along the way is up to the
implementation.

## Task Checklist

- [ ] 1. In `cache.py`, add `TTLCache.delete(key)` and `TTLCache.__len__`, which
      counts only live entries. Cover both in `test_cache.py`: a deleted key reads
      as `None`, deleting a missing key does not raise, and `len()` drops an entry
      once it expires.
