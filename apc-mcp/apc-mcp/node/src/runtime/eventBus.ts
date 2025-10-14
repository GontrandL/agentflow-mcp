import { EventEmitter } from "node:events";

export type EventPayload = Record<string, unknown>;
export const TOPIC = {
  CRC_SIGNAL: "crc.signal",
  NUDGE: "nudge.request",
  ENFORCE: "enforce.request",
  STATE: "state.transition",
} as const;

export class EventBus extends EventEmitter {
  emitTopic(topic: string, payload: EventPayload) {
    this.emit(topic, payload);
  }
  onTopic(topic: string, handler: (p: EventPayload)=>void) {
    this.on(topic, handler);
  }
}
