<script setup lang="ts">
/**
 * The trace timeline (03 FR-258): every step's id, label, consumed values, produced value,
 * matched table row key and elapsed time, then the bundle hash and the version reference.
 * Values are the platform's own, passed through as JSON; nothing is recomputed.
 */
import type { Trace } from "@/api/score";

defineProps<{ trace: Trace }>();

function show(value: unknown): string {
  return JSON.stringify(value);
}
</script>

<template>
  <section aria-labelledby="trace-heading">
    <h2
      id="trace-heading"
      class="text-lg font-medium"
    >
      Trace
    </h2>
    <p class="mt-1 text-xs text-slate-500">
      <span class="font-mono">{{ trace.rating_version_ref }}</span>
      ·
      <span class="font-mono">{{ trace.bundle_hash }}</span>
    </p>
    <ol
      class="mt-3 space-y-3"
      aria-label="Trace steps"
    >
      <li
        v-for="step in trace.steps"
        :key="step.step_id"
        class="rounded-md border border-slate-200 p-3 text-sm"
      >
        <p class="font-medium">
          {{ step.label ?? step.step_id }}
          <span class="ml-2 font-mono text-xs text-slate-500">{{ step.step_id }} · {{ step.type }}</span>
          <span class="ml-2 text-xs text-slate-500">{{ step.elapsed_us ?? 0 }} µs</span>
        </p>
        <dl class="mt-1 grid grid-cols-[8rem_1fr] gap-x-3 gap-y-0.5 font-mono text-xs">
          <dt class="text-slate-500">
            Consumed
          </dt>
          <dd>{{ show(step.consumed ?? {}) }}</dd>
          <dt class="text-slate-500">
            Produced
          </dt>
          <dd>{{ show(step.produced ?? {}) }}</dd>
          <template v-if="step.matched">
            <dt class="text-slate-500">
              Matched row
            </dt>
            <dd>{{ show(step.matched) }}</dd>
          </template>
          <template v-if="step.violation">
            <dt class="text-red-700">
              Violation
            </dt>
            <dd class="text-red-700">
              {{ show(step.violation) }}
            </dd>
          </template>
        </dl>
      </li>
    </ol>
  </section>
</template>
