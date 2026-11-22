<script setup lang="ts">
/**
 * Which artifact this is, which Job produced it, and which governed artifacts it is about
 * (FR-2159, re-widening FR-6).
 *
 * The one input is the generated `Provenance` object, which the API composes on every read
 * of the ten governed shapes. **The Job id is text, not a link** (#1869, option (a)): there
 * is no Jobs view yet (`/jobs`, `07`), and the Work that builds it adds the link here without
 * changing this component's input. A null `produced_by_job_id` says "not recorded", never a
 * blank: an empty slot would read as "no Job was involved", which nothing has established.
 */
import type { components } from "@/api/generated/schema";

type Provenance = components["schemas"]["Provenance"];

defineProps<{ provenance: Provenance }>();

// Keyed on the generated closed set, so a new `entity_type` fails the type-check here.
const ENTITY_LABEL: Record<Provenance["entity_type"], string> = {
  validation_report: "Validation report",
  profile: "Profile",
  diagnostics: "Diagnostics",
  model_comparison: "Model comparison",
  backtest: "Backtest",
  regression_run: "Regression run",
  objective_certificate: "Objective certificate",
  dislocation_run: "Dislocation run",
  metric_certificate: "Metric certificate",
  transparency_artifact: "Transparency artifact",
};

/** The parents the object could not name (`unnamed_subjects`), said in words. */
function unnamedText(count: number): string {
  const noun = count === 1 ? "governed parent" : "governed parents";
  return `${count} ${noun} could not be written as a reference`;
}
</script>

<template>
  <div
    role="group"
    aria-label="Provenance"
    class="mt-3 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-700"
  >
    <dl class="flex flex-wrap gap-x-6 gap-y-1">
      <div class="flex gap-1.5">
        <dt class="text-slate-500">
          {{ ENTITY_LABEL[provenance.entity_type] }}
        </dt>
        <dd class="font-mono">
          {{ provenance.entity_id }}
        </dd>
      </div>
      <div class="flex gap-1.5">
        <dt class="text-slate-500">
          Produced by Job
        </dt>
        <dd
          v-if="provenance.produced_by_job_id"
          class="font-mono"
        >
          {{ provenance.produced_by_job_id }}
        </dd>
        <dd
          v-else
          class="italic"
        >
          not recorded
        </dd>
      </div>
      <!-- One text node, in the object's order (FR-2159 orders the multi-ref shapes). -->
      <div
        v-if="provenance.subject_refs.length || provenance.unnamed_subjects"
        class="flex gap-1.5"
      >
        <dt class="text-slate-500">
          About
        </dt>
        <dd
          v-if="provenance.subject_refs.length"
          class="font-mono"
        >
          {{ provenance.subject_refs.join(", ") }}
        </dd>
        <!-- FR-2159's amendment of 2026-11-21 (ADR-2170): a parent whose stored
             reference cannot be read is said in words, never left blank. -->
        <dd
          v-if="provenance.unnamed_subjects"
          class="italic"
        >
          {{ unnamedText(provenance.unnamed_subjects) }}
        </dd>
      </div>
    </dl>
  </div>
</template>
