<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import RuleBuilder from "@/components/RuleBuilder.vue";
import { isProblem, ProblemError } from "@/api/problem";
import {
  approveRule,
  byLayer,
  getRuleSet,
  membersOf,
  replaceRuleSet,
  submitRule,
  type RuleSetEntry,
  type RuleSetMemberWrite,
  type Severity,
  type ValidationRule,
  type ValidationRuleSet,
} from "@/api/rules";

const props = defineProps<{ slug: string }>();

const ruleSet = ref<ValidationRuleSet | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);
const missing = ref<string | null>(null);
const acting = ref<string | null>(null);
const actionError = ref<string | null>(null);
/** The rule whose next version is being authored, or `null`. */
const versioning = ref<ValidationRule | null>(null);

const layers = computed(() => byLayer(ruleSet.value));
/**
 * FR-45: every layer must be present, and an empty one is a **configuration warning
 * surfaced here**. It comes from the API as a computed field rather than being re-derived
 * from the entries — a client that computed it would be a second implementation of the
 * rule, and the two would eventually disagree.
 */
const empty = computed<readonly string[]>(() => ruleSet.value?.empty_layers ?? []);

/**
 * The numbers the engine will use. `params` *and* `tolerance` — `01` §4.4 puts thresholds
 * in both, and showing only one would present a rule as unconfigured when it is not.
 * Targets (`key_columns`, `columns`) are not thresholds and belong in the rule's own row.
 */
function thresholds(entry: RuleSetEntry): string {
  return Object.entries({ ...(entry.rule.params ?? {}), ...(entry.rule.tolerance ?? {}) })
    .filter(([key]) => key !== "key_columns" && key !== "columns")
    .map(([key, value]) => `${key}=${value}`)
    .join(" ");
}

const SEVERITY_TONE: Record<string, string> = {
  fail: "bg-red-100 text-red-900",
  warn: "bg-amber-100 text-amber-900",
  info: "bg-slate-100 text-slate-700",
};
const STATUS_TONE: Record<string, string> = {
  draft: "bg-slate-100 text-slate-700",
  review: "bg-amber-100 text-amber-900",
  approved: "bg-emerald-100 text-emerald-900",
};

async function load(): Promise<void> {
  loading.value = true;
  problem.value = null;
  missing.value = null;
  try {
    ruleSet.value = await getRuleSet(props.slug);
  } catch (error) {
    // A dataset with no rule set is a state, not a failure: FR-45 says one must be
    // defined before a version can be validated, which is advice rather than an error.
    // The server already explains this one in FR-45's own words; repeating it here
    // in different words would be a second copy that drifts.
    if (isProblem(error, "NOT_FOUND")) missing.value = error.problem.detail ?? error.problem.title;
    else if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
}

/**
 * Edit the membership of one entry — which **replaces the set**, creating a new version
 * (FR-51). Never an edit in place: a report cites the rule-set version it ran, so
 * mutating a set would change what every past report was a report *of*.
 *
 * Built from `membersOf`, not from the ids: rebuilding the body from ids alone would
 * silently re-enable every other disabled entry and drop every other override.
 */
async function edit(entry: RuleSetEntry, change: Partial<RuleSetMemberWrite>): Promise<void> {
  if (!ruleSet.value) return;
  acting.value = entry.rule.id;
  actionError.value = null;
  const rules = membersOf(ruleSet.value).map((member) =>
    member.rule_id === entry.rule.id ? { ...member, ...change } : member,
  );
  try {
    ruleSet.value = await replaceRuleSet(props.slug, rules);
  } catch (error) {
    if (error instanceof ProblemError) actionError.value = explain(error);
    else throw error;
  } finally {
    acting.value = null;
  }
}

function explain(error: ProblemError): string {
  // `SUBMITTER_CANNOT_APPROVE` is not a permission problem — holding `approval:decide`
  // does not let you approve your own rule. The message has to say "someone else", not
  // "ask for access", or the reader goes looking for a grant they already have.
  if (error.code === "SUBMITTER_CANNOT_APPROVE") {
    return "A rule cannot be approved by its author. Someone else must review it.";
  }
  if (error.code === "RULE_SEVERITY_DOWNGRADE_FORBIDDEN") {
    return "An override may only raise severity. Deciding a failure is acceptable is a "
      + "change to the rule itself, which goes through the rule's own review.";
  }
  return `${error.problem.title}. ${error.problem.detail ?? ""}`.trim();
}

async function act(rule: ValidationRule, what: "submit" | "approve"): Promise<void> {
  acting.value = rule.id;
  actionError.value = null;
  try {
    await (what === "submit" ? submitRule(rule.id) : approveRule(rule.id));
    await load();
  } catch (error) {
    if (error instanceof ProblemError) {
      // `SUBMITTER_CANNOT_APPROVE` is not a permission problem — holding `approval:decide`
      // does not let you approve your own rule. The message has to say "someone else",
      // not "ask for access", or the reader goes looking for a grant they already have.
      // `error.code`, not `isProblem(error, …)`: inside this branch `error` is already a
      // `ProblemError`, so the type guard's *false* arm narrows it to `never` and the
      // fallback string stops compiling.
      actionError.value =
        error.code === "SUBMITTER_CANNOT_APPROVE"
          ? "A rule cannot be approved by its author. Someone else must review it."
          : `${error.problem.title}. ${error.problem.detail ?? ""}`.trim();
    } else throw error;
  } finally {
    acting.value = null;
  }
}

onMounted(() => void load());
</script>

<template>
  <section>
    <header class="mb-5">
      <p class="text-sm text-slate-500">
        <RouterLink
          to="/data"
          class="hover:underline"
        >
          Datasets
        </RouterLink>
        <span class="mx-1.5">/</span>
        <RouterLink
          :to="`/data/${slug}`"
          class="hover:underline"
        >
          {{ slug }}
        </RouterLink>
      </p>
      <h1 class="mt-1 text-xl font-semibold tracking-tight">
        Rule set
      </h1>
      <p
        v-if="ruleSet"
        class="mt-1 text-sm text-slate-500"
      >
        version {{ ruleSet.version }} · {{ ruleSet.status }} ·
        {{ (ruleSet.entries ?? []).length }} rules
      </p>
    </header>

    <p
      v-if="loading"
      class="text-sm text-slate-500"
    >
      Loading…
    </p>

    <template v-else-if="missing">
      <p class="text-sm text-slate-600">
        {{ missing }}
      </p>
      <!-- The first rule has to be authorable from here: without this, a dataset with no
           rule set is a screen that states a problem and offers nothing to do about it. -->
      <RuleBuilder
        :key="versioning?.id ?? 'new'"
        :slug="slug"
        :seed="versioning"
        @authored="load"
      />
    </template>

    <div
      v-else-if="problem"
      role="alert"
      class="rounded-md border border-red-200 bg-red-50 p-4"
    >
      <p class="font-medium text-red-900">
        {{ problem.problem.title }}
      </p>
      <p
        v-if="problem.problem.detail"
        class="mt-1 text-sm text-red-800"
      >
        {{ problem.problem.detail }}
      </p>
      <p
        v-if="problem.traceId"
        class="mt-2 font-mono text-xs text-red-700"
      >
        trace {{ problem.traceId }}
      </p>
    </div>

    <template v-else-if="ruleSet">
      <p
        v-if="empty.length"
        class="rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950"
      >
        <strong>{{ empty.length }}</strong> of the four layers
        {{ empty.length === 1 ? "has" : "have" }} no enabled rule:
        <span class="font-mono">{{ empty.join(", ").replaceAll("_", " ") }}</span>.
        A dataset with no reference tables genuinely has nothing referential to check — but
        a layer lost in an edit looks the same, and would go unnoticed.
      </p>

      <p
        v-if="actionError"
        role="alert"
        class="mt-3 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900"
      >
        {{ actionError }}
      </p>

      <section
        v-for="section in layers"
        :key="section.layer"
        class="mt-8"
      >
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          {{ section.layer.replaceAll("_", " ") }} —
          {{ section.entries.filter((e) => e.enabled).length }} enabled
          <span
            v-if="section.entries.some((e) => !e.enabled)"
            class="text-slate-400"
          >of {{ section.entries.length }}</span>
        </h2>
        <p
          v-if="!section.entries.length || empty.includes(section.layer)"
          class="mt-1 text-sm text-amber-800"
        >
          No enabled rule in this layer.
        </p>
        <!-- Not `v-else` on the warning above: a layer can be reported empty *and* hold a
             disabled rule, and chaining them would hide the very row that explains why. -->
        <table
          v-if="section.entries.length"
          :aria-label="section.layer"
          class="mt-2 w-full text-left text-sm"
        >
          <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Rule
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Check
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Severity
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Thresholds
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                State
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="entry in section.entries"
              :key="entry.rule.id"
              :class="['border-b border-slate-100', entry.enabled ? '' : 'opacity-50']"
            >
              <td class="py-2">
                <span class="font-mono text-xs">{{ entry.rule.slug }}</span>
                <span class="ml-2 text-xs text-slate-400">v{{ entry.rule.version }}</span>
                <!-- `empty_layers` counts *enabled* entries only, so a disabled rule that
                     looked like any other would contradict the banner above it. -->
                <span
                  v-if="!entry.enabled"
                  class="ml-2 rounded bg-slate-200 px-1.5 py-0.5 text-xs text-slate-600"
                >disabled</span>
                <p
                  v-if="entry.rule.rationale"
                  class="mt-0.5 text-xs text-slate-500"
                >
                  {{ entry.rule.rationale }}
                </p>
              </td>
              <td class="py-2 font-mono text-xs text-slate-600">
                {{ entry.rule.check }}
              </td>
              <td class="py-2">
                <span
                  :class="['rounded px-2 py-0.5 text-xs font-medium',
                           SEVERITY_TONE[entry.severity_override ?? entry.rule.severity]
                             ?? 'bg-slate-100']"
                >{{ entry.severity_override ?? entry.rule.severity }}</span>
                <span
                  v-if="entry.severity_override"
                  class="ml-1 text-xs text-slate-500"
                >overridden</span>
                <!-- Raise only. `warn → fail` tightens a shipped rule and needs no review;
                     the opposite is a decision that a failure is acceptable, and belongs
                     in the rule's own review where somebody reads it (FR-50). -->
                <button
                  v-if="entry.rule.severity === 'warn'"
                  type="button"
                  class="ml-2 rounded border border-slate-300 px-2 py-0.5 text-xs hover:bg-slate-50"
                  :disabled="acting === entry.rule.id"
                  @click="edit(entry, {
                    severity_override: entry.severity_override ? null : ('fail' as Severity),
                  })"
                >
                  {{ entry.severity_override ? "Clear override" : "Raise to fail" }}
                </button>
              </td>
              <!-- A threshold belongs to the rule, not to the set (`01` §4.4, corrected
                   2026-08-23). Read-only here by design: changing one authors a new rule
                   version through `FR-50`'s reviewed path, which is what the button
                   below starts. A Rule Set entry gets `enabled` and `severity_override`
                   and no third override (`FR-56`). -->
              <td class="py-2 font-mono text-xs text-slate-600">
                {{ thresholds(entry) || "—" }}
                <button
                  type="button"
                  class="ml-2 rounded border border-slate-300 px-2 py-0.5 text-xs hover:bg-slate-50"
                  @click="versioning = entry.rule"
                >
                  New version
                </button>
              </td>
              <td class="py-2">
                <span
                  :class="['rounded px-2 py-0.5 text-xs font-medium',
                           STATUS_TONE[entry.rule.status] ?? 'bg-slate-100']"
                >{{ entry.rule.status }}</span>
                <button
                  type="button"
                  class="ml-2 rounded border border-slate-300 px-2 py-0.5 text-xs hover:bg-slate-50"
                  :disabled="acting === entry.rule.id"
                  @click="edit(entry, { enabled: !entry.enabled })"
                >
                  {{ entry.enabled ? "Disable" : "Enable" }}
                </button>
                <button
                  v-if="entry.rule.status === 'draft'"
                  type="button"
                  class="ml-2 rounded border border-slate-300 px-2 py-0.5 text-xs hover:bg-slate-50"
                  :disabled="acting === entry.rule.id"
                  @click="act(entry.rule, 'submit')"
                >
                  Submit
                </button>
                <button
                  v-else-if="entry.rule.status === 'review'"
                  type="button"
                  class="ml-2 rounded border border-emerald-400 px-2 py-0.5 text-xs text-emerald-900 hover:bg-emerald-50"
                  :disabled="acting === entry.rule.id"
                  @click="act(entry.rule, 'approve')"
                >
                  Approve
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <RuleBuilder
        :key="versioning?.id ?? 'new'"
        :slug="slug"
        :seed="versioning"
        @authored="load"
      />

      <p class="mt-8 text-xs text-slate-500">
        Replacing a rule set creates a new <strong>version</strong> — never an edit in place.
        A validation report records the exact rule-set version it ran, so changing one would
        alter what every past report was a report of.
      </p>
    </template>
  </section>
</template>
