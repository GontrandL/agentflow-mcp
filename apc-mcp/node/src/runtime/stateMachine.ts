export enum State { OK="OK", WARN="WARN", SOFT="SOFT", HARD="HARD", RESCUE="RESCUE" }

type Event = "green"|"warn"|"soft"|"hard"|"rescue"|"reset";

export function nextState(cur: State, ev: Event): State {
  switch (ev) {
    case "green":  return (cur===State.OK||cur===State.WARN) ? State.OK : cur;
    case "warn":   return cur===State.OK ? State.WARN : cur;
    case "soft":   return (cur===State.OK||cur===State.WARN) ? State.SOFT : cur;
    case "hard":   return State.HARD;
    case "rescue": return State.RESCUE;
    case "reset":  return State.OK;
    default:       return cur;
  }
}
