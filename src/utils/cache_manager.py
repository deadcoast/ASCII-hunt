"""Cache Manager Module."""

# Import TypeVar for generic types
from typing import Any, Generic, TypeVar

# Define type variables for generic LRUCache
KT = TypeVar("KT")  # Key Type
VT = TypeVar("VT")  # Value Type


class CacheManager:
    """Cache Manager Class.

    This class provides a CacheManager class for managing caches.
    """

    def __init__(self, max_size: int = 100) -> None:
        """Initialize a CacheManager.

        :param max_size: The maximum size of each cache.
        :type max_size: int
        """
        self.max_size = max_size
        # Use the locally defined LRUCache
        self.caches: dict[str, LRUCache[Any, Any]] = {}

    # Make create_if_missing keyword-only and adjust return type
    def get_cache(
        self, name: str, *, create_if_missing: bool = True
    ) -> "LRUCache[Any, Any] | None":
        """Get a cache by name."""
        if name not in self.caches and create_if_missing:
            self.caches[name] = LRUCache[Any, Any](self.max_size)

        return self.caches.get(name)

    def clear_cache(self, name: str | None = None) -> None:
        """Clear a cache or all caches."""
        if name is None:
            for cache in self.caches.values():
                cache.clear()

        elif name in self.caches:
            self.caches[name].clear()

    # Adjust return type
    def get_cache_stats(self, name: str | None = None) -> dict[str, Any] | None:
        """Get cache statistics."""
        if name is not None:
            return self.caches[name].get_stats() if name in self.caches else None
        return {name: cache.get_stats() for name, cache in self.caches.items()}


# Make the local LRUCache generic
class LRUCache(Generic[KT, VT]):
    """LRU Cache Class.

    This class provides a LRUCache class for managing caches.
    """

    def __init__(self, max_size: int = 100) -> None:
        """Initialize a LRUCache.

        :param max_size: The maximum size of the cache.
        :type max_size: int
        """
        self.max_size = max_size
        self.cache: dict[KT, VT] = {}
        self.order: list[KT] = []
        self.hits = 0
        self.misses = 0

    def get(self, key: KT, default: VT | None = None) -> VT | None:
        """Get a value from the cache."""
        if key in self.cache:
            self.order.remove(key)
            self.order.append(key)
            self.hits += 1
            return self.cache[key]

        self.misses += 1
        return default

    def put(self, key: KT, value: VT) -> None:
        """Put a value in the cache."""
        if key in self.cache:
            self.cache[key] = value
            self.order.remove(key)
        else:
            if len(self.cache) >= self.max_size:
                lru_key = self.order.pop(0)
                del self.cache[lru_key]
            self.cache[key] = value

        self.order.append(key)

    def clear(self) -> None:
        """Clear the cache."""
        self.cache = {}
        self.order = []

    def get_stats(self) -> dict[str, Any]:
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
