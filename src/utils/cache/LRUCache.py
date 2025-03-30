"""LRUCache Module."""

from collections import OrderedDict
from collections.abc import Iterator
from typing import Any


class LRUCache:
    """Lru Cache Class."""

    def __init__(self, max_size: int = 100) -> None:
        """Initialize a LRUCache.

        :param max_size: The maximum size of the cache.
        :type max_size: int
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, Any] = OrderedDict()

    def get(self, key: str) -> Any | None:
        """Get a value from the cache.

        :param key: The key to get the value from.
        :type key: str
        :return: The value from the cache.
        :rtype: Any
        """
        if key not in self.cache:
            return None

        value = self.cache.pop(key)
        self.cache[key] = value
        return value

    def get_all(self) -> Iterator[tuple[str, Any]]:
        """Get all values from the cache.

        :return: An iterator of all values in the cache.
        :rtype: Iterator[tuple[str, Any]]
        """
        return iter(self.cache.items())

    def put(self, key: str, value: Any) -> None:
        """Put a value into the cache.

        :param key: The key to put the value into.
        :type key: str
        :param value: The value to put into the cache.
        :type value: Any
        """
        if key in self.cache:
            self.cache.pop(key)

        self.cache[key] = value
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get the stats of the cache.

        :return: The stats of the cache.
        :rtype: dict
        """
        return {"size": len(self.cache), "max_size": self.max_size}

    def __len__(self) -> int:
        """Get the size of the cache.

        :return: The size of the cache.
        :rtype: int
        """
        return len(self.cache)

    def __contains__(self, key: str) -> bool:
        """Check if the cache contains a key.

        :param key: The key to check if the cache contains.
        :type key: str
        """
        return key in self.cache

    def __iter__(self) -> Iterator[str]:
        """Iterate over the cache."""
        return iter(self.cache)

    def __repr__(self) -> str:
        """Represent the cache."""
        return f"LRUCache(size={len(self)}, max_size={self.max_size})"

    def __str__(self) -> str:
        """String representation of the cache."""
        return str(self.cache)

    def __eq__(self, other: object) -> bool:
        """Check if the cache is equal to another object."""
        return self.cache == other.cache if isinstance(other, LRUCache) else False

    def __ne__(self, other: object) -> bool:
        """Check if the cache is not equal to another object."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Hash the cache."""
        return hash(self.cache)
