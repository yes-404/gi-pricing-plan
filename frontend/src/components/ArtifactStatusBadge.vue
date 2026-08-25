<script setup lang="ts">
/**
 * The lifecycle status of a Custom Objective or a Custom Metric.
 *
 * One badge for both because FR-MODEL-45 makes it one lifecycle — `MetricStatus` is
 * `ObjectiveStatus`'s five members, declared separately. The prop is typed on the union of
 * both rather than on either: the members are equal today, and a `Record` over the union
 * breaks at compile time if one side ever gains a member the other lacks, which is exactly
 * when a shared badge would otherwise start rendering an unstyled status.
 *
 * **Not a ladder.** FR-MODEL-46 writes the lifecycle with arrows, but
 * `VALID_OBJECTIVE_TRANSITIONS` in `model_schema/objectives.py` permits
 * `review → {approved, certified}` and `certified → {review, draft, deprecated}`. Nothing here
 * or in any caller may present these five as a sequence — no numbered steps, no progress bar,
 * no ordering that implies one follows another.
 */
import type { ObjectiveStatus } from "@/api/objectives";
import type { MetricStatus } from "@/api/metrics";

type ArtifactStatus = ObjectiveStatus | MetricStatus;

defineProps<{ status: ArtifactStatus }>();

const TONE: Record<ArtifactStatus, string> = {
  draft: "bg-slate-100 text-slate-700",
  certified: "bg-sky-100 text-sky-800",
  review: "bg-amber-100 text-amber-900",
  approved: "bg-emerald-100 text-emerald-800",
  deprecated: "bg-slate-200 text-slate-500",
};
</script>

<template>
  <span :class="['rounded px-2 py-0.5 text-xs font-medium', TONE[status]]">{{ status }}</span>
</template>
