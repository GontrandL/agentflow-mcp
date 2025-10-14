from enum import Enum
from typing import Literal, Tuple

class State(str, Enum):
    OK="OK"; WARN="WARN"; SOFT="SOFT"; HARD="HARD"; RESCUE="RESCUE"

Transition = Tuple[State, State, str]

def next_state(cur: State, event: Literal["green","warn","soft","hard","rescue","reset"]) -> State:
    # minimal deterministic policy
    if event == "green":
        return State.OK if cur in (State.OK, State.WARN) else cur
    if event == "warn":
        return State.WARN if cur == State.OK else cur
    if event == "soft":
        return State.SOFT if cur in (State.OK, State.WARN) else cur
    if event == "hard":
        return State.HARD
    if event == "rescue":
        return State.RESCUE
    if event == "reset":
        return State.OK
    return cur
