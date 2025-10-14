from collections import OrderedDict
from typing import Any, Optional

class LRUCache:
    def __init__(self, capacity: int = 512) -> None:
        self.capacity = capacity
        self._d: OrderedDict[str, Any] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key in self._d:
            self._d.move_to_end(key)
            return self._d[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._d[key] = value
        self._d.move_to_end(key)
        if len(self._d) > self.capacity:
            self._d.popitem(last=False)

    def __contains__(self, key: str) -> bool:
        return key in self._d
