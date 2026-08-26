<script setup lang="ts">
import { computed } from "vue";

import type { RuleResult } from "@/api/validation";

const props = defineProps<{ result: RuleResult }>();
defineEmits<{ acknowledge: [result: RuleResult] }>();

const OUTCOME_TONE: Record<string, string> = {
  fail: "bg-red-100 text-red-900",
  error: "bg-red-100 text-red-900",
  warn: "bg-amber-100 text-amber-900",
  pass: "bg-emerald-100 text-emerald-900",
  skipped: "bg-slate-100 text-slate-700",
};

/**
 * Measured against threshold, side by side.
 *
 * `01` §5.3 asks for both because one without the other is unactionable: "PSI 0.31" means
 * nothing until you know the rule warns above 0.10, and "warns above 0.10" means nothing
 * without the number it measured.
 */
const measured = computed(() => Object.entries(props.result.measured ?? {}));
const threshold = computed(() => Object.entries(props.result.threshold ?? {}));

function format(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (Array.isArray(value)) return value.length > 4
    ? `${value.slice(0, 4).join(", ")} … (${value.length})`
    : value.join(", ");
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
</script>

<template>
  <article class="border-b border-slate-100 py-4">
    <header class="flex items-baseline gap-3">
      <span
        :class="['rounded px-2 py-0.5 text-xs font-medium uppercase tracking-wide',
                 OUTCOME_TONE[result.outcome] ?? 'bg-slate-100']"
      >{{ result.outcome }}</span>
      <h3 class="font-medium">
        {{ result.rule_slug }}
      </h3>
      <span class="text-xs text-slate-500">
        {{ result.layer.replace("_", " ") }} · v{{ result.rule_version }}
      </span>
      <button
        v-if="result.outcome === 'warn' && !result.acknowledgement"
        type="button"
        class="ml-auto rounded-md border border-amber-400 bg-white px-2.5 py-1 text-xs font-medium text-amber-900 hover:bg-amber-50"
        @click="$emit('acknowledge', result)"
      >
        Acknowledge…
      </button>
    </header>

    <p
      v-if="result.detail"
      class="mt-1.5 text-sm text-slate-700"
    >
      {{ result.detail }}
    </p>

    <p
      v-if="result.error_reason"
      class="mt-1.5 text-sm text-red-800"
    >
      The rule did not run: {{ result.error_reason }}. An unrun rule is never a pass.
    </p>

    <dl
      v-if="measured.length || threshold.length"
      class="mt-2 flex flex-wrap gap-x-6 gap-y-1 text-xs"
    >
      <div
        v-for="[key, value] in measured"
        :key="`m-${key}`"
        class="flex gap-1.5"
      >
        <dt class="text-slate-500">
          {{ key }}
        </dt>
        <dd class="font-mono tabular-nums">
          {{ format(value) }}
        </dd>
      </div>
      <div
        v-for="[key, value] in threshold"
        :key="`t-${key}`"
        class="flex gap-1.5"
      >
        <dt class="text-slate-400">
          {{ key }} (threshold)
        </dt>
        <dd class="font-mono tabular-nums text-slate-600">
          {{ format(value) }}
        </dd>
      </div>
    </dl>

    <p
      v-if="result.affected_rows"
      class="mt-2 text-xs text-slate-600 tabular-nums"
    >
      {{ result.affected_rows.toLocaleString() }} affected row(s)
      <template v-if="result.affected_exposure_fraction != null">
        · {{ (result.affected_exposure_fraction * 100).toFixed(2) }}% of exposure
      </template>
    </p>

    <details
      v-if="(result.offending_sample ?? []).length"
      class="mt-2"
    >
      <summary class="cursor-pointer text-xs text-slate-600">
        Offending sample ({{ (result.offending_sample ?? []).length }} row(s))
      </summary>
      <ul class="mt-1 max-h-40 overflow-y-auto font-mono text-xs text-slate-700">
        <li
          v-for="(item, index) in result.offending_sample"
          :key="index"
        >
          {{ Object.entries(item).map(([column, value]) => `${column}: ${value ?? 'null'}`).join('  ') }}
        </li>
      </ul>
    </details>

    <p
      v-if="result.acknowledgement"
      class="mt-2 rounded bg-slate-50 px-3 py-2 text-xs text-slate-700"
    >
      Acknowledged {{ new Date(result.acknowledgement.at).toLocaleString() }} —
      “{{ result.acknowledgement.justification }}”
    </p>
  </article>
</template>
