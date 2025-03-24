"""Cache Manager Module."""

from collections import OrderedDict


class CacheManager:
    def __init__(self, max_size=100):
        """
        Initialize a CacheManager.

        :param max_size: The maximum size of each cache.
        :type max_size: int
        """
        self.max_size = max_size
        self.caches = {}

    def get_cache(self, name, create_if_missing=True):
        """Get a cache by name."""
        if name not in self.caches and create_if_missing:
            self.caches[name] = LRUCache(self.max_size)

        return self.caches.get(name)

    def clear_cache(self, name=None):
        """Clear a cache or all caches."""
        if name is not None:
            if name in self.caches:
                self.caches[name].clear()
        else:
            for cache in self.caches.values():
                cache.clear()

    def get_cache_stats(self, name=None):
        """Get cache statistics."""
        if name is not None:
            if name in self.caches:
                return self.caches[name].get_stats()
            return None

        stats = {}
        for name, cache in self.caches.items():
            stats[name] = cache.get_stats()

        return stats


class LRUCache:
    def __init__(self, max_size=100):
        self.max_size = max_size
        self.cache = {}
        self.order = []
        self.hits = 0
        self.misses = 0

    def get(self, key, default=None):
        """Get a value from the cache."""
        if key in self.cache:
            # Move to end of order (most recently used)
            self.order.remove(key)
            self.order.append(key)

            self.hits += 1
            return self.cache[key]

        self.misses += 1
        return default

    def put(self, key, value):
        """Put a value in the cache."""
        if key in self.cache:
            # Update existing entry
            self.cache[key] = value

            # Move to end of order (most recently used)
            self.order.remove(key)
            self.order.append(key)
        else:
            # Add new entry
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                lru_key = self.order.pop(0)
                del self.cache[lru_key]

            self.cache[key] = value
            self.order.append(key)

    def clear(self):
        """Clear the cache."""
        self.cache = {}
        self.order = []

    def get_stats(self):
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
        }
