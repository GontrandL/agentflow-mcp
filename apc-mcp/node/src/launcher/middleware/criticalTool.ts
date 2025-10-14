/**
 * Critical tool guard for the local launcher.
 * Wraps tool execution and tags "critical" calls (write/edit/bash/network/pkg_install/test_run/deploy).
 */
type ToolName =
  | "read" | "search" | "write" | "edit" | "bash" | "network"
  | "pkg_install" | "test_run" | "deploy";

export interface ToolCall {
  tool: ToolName;
  args: Record<string, unknown>;
}

export interface Policy {
  allow: ToolName[];
  writeScope?: string[];           // e.g. ["src/**"]
  maxTestTimeoutSec?: number;      // e.g. 480
}

export type EnforceResult =
  | { ok: true; critical: boolean }
  | { ok: false; reason: string };

const CRITICAL: ToolName[] = ["write","edit","bash","network","pkg_install","test_run","deploy"];

export function enforceToolPolicy(call: ToolCall, policy: Policy): EnforceResult {
  if (!policy.allow.includes(call.tool)) return { ok: false, reason: "tool_forbidden" };

  // example guardrails
  if (call.tool === "test_run" && typeof call.args["timeout"] === "number") {
    if (policy.maxTestTimeoutSec && (call.args["timeout"] as number) > policy.maxTestTimeoutSec) {
      return { ok: false, reason: "timeout_exceeds_policy" };
    }
  }
  // scope checks for write/edit are launcher-specific (path allowlist)
  const critical = CRITICAL.includes(call.tool);
  return { ok: true, critical };
}
