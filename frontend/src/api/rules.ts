import { request } from "./client";
import type { components } from "./generated/schema";
import { pageThrough, type Paged } from "./paging";

export type ValidationRuleSet = components["schemas"]["ValidationRuleSet"];
export type ValidationRule = components["schemas"]["ValidationRule"];
export type RuleSetEntry = components["schemas"]["RuleSetEntry"];
export type ValidationLayer = components["schemas"]["ValidationLayer"];
export type RuleSetMemberWrite = components["schemas"]["RuleSetMemberWrite"];
export type Severity = components["schemas"]["Severity"];
export type RuleCreate = components["schemas"]["RuleCreate"];

/** The four layers, in the order `01` §3.3 and §4.4 present them. */
export const LAYERS: readonly ValidationLayer[] = [
  "structural",
  "referential",
  "actuarial_sanity",
  "distributional",
];

export function getRuleSet(slug: string): Promise<ValidationRuleSet> {
  return request<ValidationRuleSet>(`/datasets/${encodeURIComponent(slug)}/rule-set`);
}

/**
 * Replace the rule set, which creates a **new version** (FR-DATA-22).
 *
 * Never an edit in place: a Validation Report records the exact `rule_set_version` it ran,
 * so mutating a set would change what every past report was a report *of* — and "it passed"
 * would stop meaning "it passed these rules".
 */
export function replaceRuleSet(
  slug: string,
  rules: RuleSetMemberWrite[],
  referenceVersionId?: string,
): Promise<ValidationRuleSet> {
  return request<ValidationRuleSet>(`/datasets/${encodeURIComponent(slug)}/rule-set`, {
    method: "PUT",
    body: { rules, reference_dataset_version_id: referenceVersionId ?? null },
  });
}

/**
 * The set as it stands, in the shape a replace takes — the starting point for any edit.
 *
 * A caller that rebuilt this from ids alone would silently re-enable every disabled entry
 * and drop every override, because those fields would simply be absent from the body.
 */
export function membersOf(ruleSet: ValidationRuleSet): RuleSetMemberWrite[] {
  return (ruleSet.entries ?? []).map((entry) => ({
    rule_id: entry.rule.id,
    enabled: entry.enabled,
    // `?? null`, not the value as read: `exactOptionalPropertyTypes` distinguishes absent
    // from null, and an absent field would read on the server as "no override asked for"
    // rather than "no override" — the same outcome here, but not the same statement.
    severity_override: entry.severity_override ?? null,
  }));
}

/**
 * Step 1 of `FR-DATA-21`'s chain. The body is the **generated** `RuleCreate` and is never
 * restated here: it carries `catalogue_id`, which is what records that a workspace rule
 * descends from a built-in (`FR-DATA-53`), and a hand-written copy of this shape is exactly
 * how that field failed to reach the browser once already.
 *
 * Re-using an existing rule's `slug` is not an error — the platform allocates the next
 * version, which is `FR-DATA-54`'s path for a threshold change.
 */
export function createRule(body: RuleCreate): Promise<ValidationRule> {
  return request<ValidationRule>("/validation-rules", { method: "POST", body });
}

/** Step 2: **202** with a Job. A rule cannot be approved until it has run somewhere. */
export function dryRun(ruleId: string, datasetVersionId: string): Promise<unknown> {
  return request(`/validation-rules/${ruleId}/dry-run`, {
    method: "POST",
    body: { dataset_version_id: datasetVersionId },
  });
}

/** Step 3: `draft` → `review`, and only with a dry run attached. */
export function submitRule(ruleId: string): Promise<ValidationRule> {
  return request<ValidationRule>(`/validation-rules/${ruleId}/submit`, { method: "POST" });
}

/**
 * Step 3 concluded: `review` → `approved`, by someone other than the author.
 *
 * `SUBMITTER_CANNOT_APPROVE` is the refusal to expect, and it is not a permission problem —
 * holding `approval:decide` does not let you approve your own rule. The message must say
 * "someone else", not "ask for access".
 */
export function approveRule(ruleId: string): Promise<ValidationRule> {
  return request<ValidationRule>(`/validation-rules/${ruleId}/approve`, { method: "POST" });
}

/**
 * Five pages of 200. The built-in catalogue is 38 rules (`01` §4.4) and workspace-authored
 * rules are hand-governed artifacts, so a thousand is far beyond any plausible set — and
 * `truncated` in the return type still tells a caller the sweep stopped early, rather than
 * letting a truncated page read as the whole population.
 */
export const RULES_PAGE_CAP = 5;

/**
 * The workspace's rules (`01` §5.1, `GET /api/v1/validation-rules`), cursor-paginated.
 * `builtin: true` returns §4.4's shipped catalogue only, which is the population the PSI
 * banding reads VR-DST-1's `warn_above` from.
 */
export async function listRules(
  options: { builtin?: boolean | null } = {},
): Promise<Paged<ValidationRule>> {
  return pageThrough<ValidationRule>(
    "/validation-rules",
    {
      builtin:
        options.builtin === undefined || options.builtin === null
          ? undefined
          : String(options.builtin),
    },
    RULES_PAGE_CAP,
  );
}

/** Group a rule set's entries by layer, keeping `01`'s order and every layer present. */
export function byLayer(
  ruleSet: ValidationRuleSet | null,
): { layer: ValidationLayer; entries: RuleSetEntry[] }[] {
  const entries = ruleSet?.entries ?? [];
  return LAYERS.map((layer) => ({
    layer,
    entries: entries.filter((entry) => entry.rule.layer === layer),
  }));
}
