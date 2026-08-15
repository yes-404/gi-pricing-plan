<script setup lang="ts">
import { computed } from "vue";

import { groupIntoBands, type ValidationReport } from "@/api/validation";

const props = defineProps<{ report: ValidationReport }>();

const bands = computed(() => groupIntoBands(props.report));
const blocking = computed(() => bands.value.blocking.length);
const needsAck = computed(() => bands.value["needs-acknowledgement"].length);

/**
 * The answer to "why can I not fit a model on this?", in one line.
 *
 * Three states rather than two, because "nothing failed but somebody must sign it off" is
 * a different action from "fix the data" — and telling a user only that they are blocked
 * makes them go looking for a failure that is not there.
 */
const state = computed(() => {
  if (blocking.value > 0) return "blocked" as const;
  if (needsAck.value > 0) return "awaiting" as const;
  return "clear" as const;
});

const headline = computed(() => {
  switch (state.value) {
    case "blocked":
      return `${blocking.value} rule${blocking.value === 1 ? "" : "s"} must pass before a model can be fitted`;
    case "awaiting":
      return `${needsAck.value} warning${needsAck.value === 1 ? "" : "s"} need an actuary's acknowledgement`;
    default:
      return "This version is ready to model on";
  }
});

const explanation = computed(() => {
  switch (state.value) {
    case "blocked":
      // `01` §1.3, said plainly. A user who believes a rule is wrong needs to know the
      // remedy is the rule, not a button they have not found.
      return "There is no override. If a failing rule is wrong, change the rule — that change is reviewed and audited.";
    case "awaiting":
      return "A Pricing Actuary must acknowledge each warning with a justification, which is recorded in the audit log.";
    default:
      return "No rule failed, and every warning has been acknowledged.";
  }
});

const tone = computed(() => {
  switch (state.value) {
    case "blocked":
      return "border-red-300 bg-red-50 text-red-950";
    case "awaiting":
      return "border-amber-300 bg-amber-50 text-amber-950";
    default:
      return "border-emerald-300 bg-emerald-50 text-emerald-950";
  }
});
</script>

<template>
  <div
    :class="['rounded-lg border p-5', tone]"
    role="status"
    :data-state="state"
  >
    <p class="text-base font-semibold">
      {{ headline }}
    </p>
    <p class="mt-1 text-sm opacity-90">
      {{ explanation }}
    </p>
    <dl class="mt-4 flex gap-8 text-sm">
      <div>
        <dt class="opacity-70">
          Rules run
        </dt>
        <dd class="font-medium tabular-nums">
          {{ (report.results ?? []).length }}
        </dd>
      </div>
      <div>
        <dt class="opacity-70">
          Blocking
        </dt>
        <dd class="font-medium tabular-nums">
          {{ blocking }}
        </dd>
      </div>
      <div>
        <dt class="opacity-70">
          Awaiting acknowledgement
        </dt>
        <dd class="font-medium tabular-nums">
          {{ needsAck }}
        </dd>
      </div>
      <div>
        <dt class="opacity-70">
          Rule set
        </dt>
        <dd class="font-medium tabular-nums">
          v{{ report.rule_set_version }}
        </dd>
      </div>
    </dl>
  </div>
</template>
