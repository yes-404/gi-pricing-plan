import { parseModelRef } from "./comparisons";
import type { Factor, Model } from "./models";

export interface RequiredColumns {
  /** The dataset columns one input row must carry, sorted for a stable form order. */
  readonly columns: string[];
  /**
   * The offset model to resolve and union in, or null. Non-null means this result is
   * **incomplete** on its own: see the note on `offset.kind === "model"` below.
   */
  readonly offsetModelRef: { slug: string; version: number } | null;
  /** Pinned factor ids not present in the supplied map. Surfaced, never dropped. */
  readonly unresolvedFactorIds: string[];
}

/**
 * The columns one prediction row must carry for this model.
 *
 * Pure and one-model-at-a-time. Three things make the obvious version wrong:
 *
 * 1. **`spec.factors` holds ids, not columns.** They are resolved through `factorsById`.
 *
 * 2. **An `interaction` Factor sources no columns of its own** — `model_schema` *validates*
 *    that it names none, because "its columns are its operands'". The operands are published
 *    as `operand_factor_ids` and are **not** in `spec.factors`; the backend's `load_factors`
 *    expands them transitively and records that "one level of expansion is enough". This
 *    does the same one level, so the two agree by construction of the same rule rather than
 *    by coincidence.
 *
 * 3. **`offset.kind === "model"` needs the referenced model's columns too.** The backend
 *    resolves that model per request and computes its linear predictor **on the frame the
 *    caller sent**. Its factors' columns are therefore caller-supplied, and a form built
 *    from the central model alone fails every time with `MODEL_TERM_UNRESOLVED`. This
 *    function cannot fetch, so it returns the ref and the caller unions the second result.
 */
export function requiredColumns(
  model: Model,
  factorsById: ReadonlyMap<string, Factor>,
): RequiredColumns {
  const spec = model.spec;
  const columns = new Set<string>();
  const unresolved: string[] = [];

  const take = (factorId: string, expandOperands: boolean): void => {
    const factor = factorsById.get(factorId);
    if (factor === undefined) {
      unresolved.push(factorId);
      return;
    }
    for (const column of factor.source_columns ?? []) columns.add(column);
    // One level, matching `load_factors`. An operand that is itself an interaction is
    // refused at resolution on the server, which is where that message belongs.
    if (expandOperands) {
      for (const operandId of factor.operand_factor_ids ?? []) take(operandId, false);
    }
  };

  for (const factorId of spec.factors ?? []) take(factorId, true);

  const offset = "offset" in spec ? spec.offset : undefined;
  let offsetModelRef: RequiredColumns["offsetModelRef"] = null;
  if (offset !== undefined && offset !== null) {
    if ((offset.kind === "log_column" || offset.kind === "column") && offset.column) {
      columns.add(offset.column);
    }
    if (offset.kind === "model" && offset.offset_model_ref) {
      // The same ID-3 pattern the contract publishes on `offset_model_ref`. Parsed by the
      // existing helper rather than a second copy of the regex (`CLAUDE.md` §2).
      offsetModelRef = parseModelRef(offset.offset_model_ref);
    }
  }

  return { columns: [...columns].sort(), offsetModelRef, unresolvedFactorIds: unresolved };
}
