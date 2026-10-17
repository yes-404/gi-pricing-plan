/**
 * The label a compare row carries for one StepChange (03 FR-262, §4.10; RL-1261).
 * `own_change: false` means the step's definition is the same on both sides and it moved only
 * through what it consumed. No label says "unchanged" or "not edited" (PL-1286 item 8).
 */
import type { StepChange } from "@/api/score";

export function stepChangeLabel(change: StepChange): string {
  if (change.change === "added") return "Added in comparison";
  if (change.change === "removed") return "Removed in comparison";
  if (!change.own_change) return "Changed through its inputs";
  return (change.changed_fields ?? []).includes("consumed")
    ? "Edited; its inputs also changed"
    : "Edited";
}
