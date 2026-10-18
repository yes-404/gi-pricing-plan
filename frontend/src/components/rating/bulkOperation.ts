/**
 * A bulk-operation request built from what the form holds (FR-233, `04` §4.4). Decimals stay the
 * strings typed, trimmed (FR-10); a key filter is typed one key column per line. Whether the values
 * are valid decimals, or the columns and levels exist, is the platform's to say (FR-234), so this
 * only checks that a value was given at all.
 */
import type { BulkOperationRequest } from "@/api/rateTables";

export type BulkKind = BulkOperationRequest["kind"];

export const BULK_KINDS: readonly { kind: BulkKind; label: string; fields: readonly BulkField[] }[] = [
  { kind: "uplift_table", label: "Uplift the whole table", fields: ["percentage"] },
  { kind: "uplift_by_filter", label: "Uplift the cells a key filter selects", fields: ["percentage", "filter"] },
  { kind: "floor_and_cap", label: "Floor and cap the values", fields: ["floor", "cap"] },
  { kind: "rebase_to_level", label: "Rebase to a base level", fields: ["base_level"] },
];

export type BulkField = "percentage" | "filter" | "floor" | "cap" | "base_level";

/** `area: A, B` per line → `{ area: ["A", "B"] }`; a line without a colon or a level is refused by number. */
export function parseKeyLevels(text: string): Record<string, string[]> {
  const parsed: Record<string, string[]> = {};
  text.split("\n").forEach((line, index) => {
    if (line.trim() === "") return;
    const at = line.indexOf(":");
    const column = at === -1 ? "" : line.slice(0, at).trim();
    const levels = at === -1 ? [] : line.slice(at + 1).split(",").map((level) => level.trim()).filter((level) => level !== "");
    if (column === "" || levels.length === 0) {
      throw new Error(`line ${index + 1}: write a key column, a colon, then its levels separated by commas`);
    }
    parsed[column] = levels;
  });
  return parsed;
}

function given(values: Partial<Record<BulkField, string>>, field: BulkField): string {
  const value = (values[field] ?? "").trim();
  if (value === "") throw new Error(`${field} is required`);
  return value;
}

export function buildBulkRequest(kind: BulkKind, values: Partial<Record<BulkField, string>>): BulkOperationRequest {
  switch (kind) {
    case "uplift_table":
      return { kind, parameters: { percentage: given(values, "percentage") } };
    case "uplift_by_filter":
      return {
        kind,
        parameters: { percentage: given(values, "percentage"), filter: parseKeyLevels(given(values, "filter")) },
      };
    case "floor_and_cap":
      return { kind, parameters: { floor: given(values, "floor"), cap: given(values, "cap") } };
    case "rebase_to_level":
      return { kind, parameters: { base_level: parseKeyLevels(given(values, "base_level")) } };
  }
}
