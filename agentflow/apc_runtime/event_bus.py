# Minimal in-proc event bus (no deps)
from collections import defaultdict
from typing import Callable, Dict, List, Any

class EventBus:
    def __init__(self) -> None:
        self._subs: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)

    def on(self, topic: str, handler: Callable[[Any], None]) -> None:
        self._subs[topic].append(handler)

    def emit(self, topic: str, payload: Any) -> None:
        for h in list(self._subs.get(topic, [])):
            try:
                h(payload)
            except Exception as e:
                # never crash the bus
                print(f"[event_bus] handler error on '{topic}': {e}")

# example topics (convention)
TOPIC_CRC_SIGNAL = "crc.signal"       # {layer, kind, value, context_ref}
TOPIC_NUDGE      = "nudge.request"    # {severity, message, scope}
TOPIC_ENFORCE    = "enforce.request"  # {ticket_id, tool, args, critical}
TOPIC_STATE      = "state.transition" # {from, to, reason}
