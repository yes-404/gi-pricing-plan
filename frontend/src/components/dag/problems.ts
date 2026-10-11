import type { RatingStep } from "@/api/ratingAlgorithms";

/**
 * The required-field gaps that block a save (03 §3.2). Presence checks of fields the shape
 * requires, shown before the round trip: not graph rules, and they repeat no server check
 * (RL-1474 item 2 keeps those on the server, S3's).
 */
export function stepProblems(step: RatingStep): string[] {
  const found: string[] = [];
  if (step.type === "lookup" && step.as_at.trim() === "") {
    found.push("as_at is required (FR-221)");
  }
  if (step.type === "table" && step.rate_table_ref.trim() === "") {
    found.push("rate_table_ref is required (FR-220)");
  }
  if (step.type === "constraint" && step.reason_code.trim() === "") {
    found.push("reason_code is required (FR-225)");
  }
  if (step.type === "output") {
    if (step.rounding.mode.trim() === "") found.push("rounding mode is required (FR-226)");
    if (!Number.isInteger(step.rounding.dp)) found.push("rounding dp is required (FR-226)");
  }
  return found;
}
