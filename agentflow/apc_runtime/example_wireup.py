from agentflow.apc_runtime.event_bus import EventBus, TOPIC_CRC_SIGNAL, TOPIC_NUDGE, TOPIC_STATE
from agentflow.apc_runtime.state_machine import State, next_state
from agentflow.apc_runtime.lru import LRUCache

bus = EventBus()
state = State.OK
lru = LRUCache(capacity=512)

def on_crc_signal(msg):
    global state
    # msg: {layer, kind:'drift|fidelity|evidence', value:float, context_ref:str}
    if msg["kind"] == "drift" and msg["value"] > 0.10:
        s2 = next_state(state, "soft")
        bus.emit(TOPIC_NUDGE, {"severity":"soft","message":"Focus drift detected","scope":msg["layer"]})
        bus.emit(TOPIC_STATE, {"from":state, "to":s2, "reason":"drift_soft"})
        state = s2

bus.on(TOPIC_CRC_SIGNAL, on_crc_signal)
