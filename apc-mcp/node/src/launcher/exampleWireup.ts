import { EventBus, TOPIC } from "../runtime/eventBus";
import { State, nextState } from "../runtime/stateMachine";
import { enforceToolPolicy } from "./middleware/criticalTool";

const bus = new EventBus();
let state = State.OK;

bus.on(TOPIC.CRC_SIGNAL, (msg:any) => {
  if (msg.kind === "drift" && msg.value > 0.10) {
    const to = nextState(state, "soft");
    bus.emit(TOPIC.NUDGE, { severity:"soft", message:"Focus drift detected", scope: msg.layer });
    bus.emit(TOPIC.STATE, { from: state, to, reason: "drift_soft" });
    state = to;
  }
});

// Example tool invocation interception
function runTool(call: {tool:any,args:any}) {
  const res = enforceToolPolicy(call as any, {
    allow: ["read","search","write","edit","bash","test_run"],
    maxTestTimeoutSec: 480
  });
  if (!res.ok) throw new Error(`PolicyDenied:${(res as any).reason}`);
  if (res.critical) {
    bus.emit(TOPIC.ENFORCE, { tool: call.tool, args: call.args, critical: true });
  }
  // ...execute tool here...
}
