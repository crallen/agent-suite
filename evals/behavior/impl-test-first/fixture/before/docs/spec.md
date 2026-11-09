# TTL cache fixes

## Tasks

1. **ttl=0 entries never expire.** Entries in a `TTLCache(ttl=0)` are returned by
   `get` long after they were set. Callers pass `ttl=0` to switch caching off, so
   every `get` on such a cache should miss. `ttl=None` keeps its meaning: entries
   that never expire.
