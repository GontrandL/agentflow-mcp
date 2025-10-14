#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=python/src:${PYTHONPATH:-}
source python/.venv/bin/activate 2>/dev/null || true
python3 - <<'PY'
from apc_runtime.event_bus import EventBus, TOPIC_CRC_SIGNAL, TOPIC_NUDGE, TOPIC_STATE
from apc_runtime.state_machine import State, next_state
bus = EventBus()
state = State.OK
def on_crc(msg):
    global state
    if msg.get("kind")=="drift" and msg.get("value",0)>0.10:
        ns = next_state(state, "soft")
        bus.emit(TOPIC_NUDGE, {"severity":"soft","message":"Focus drift detected","scope":msg["layer"]})
        bus.emit(TOPIC_STATE, {"from":state,"to":ns,"reason":"drift_soft"})
        state = ns
bus.on(TOPIC_CRC_SIGNAL, on_crc)
# simulate
bus.emit(TOPIC_CRC_SIGNAL, {"layer":"section.relevant_files","kind":"drift","value":0.12})
print(f"[MCP Stub] Final state: {state}")
PY
