<script setup lang="ts">
/**
 * The lifecycle status of a Custom Objective, a Custom Metric or a Peril Structure.
 *
 * **These are not one lifecycle, and the badge does not claim they are.** FR-154 makes
 * objectives and metrics share theirs — `MetricStatus` is `ObjectiveStatus`'s five members,
 * declared separately. FR-191 gives a Peril Structure a *different* one: it has
 * `reconciled`, `superseded` and `archived`, and no `certified` or `deprecated`. The prop is
 * typed on the union of all three so that a `Record` over it breaks at compile time the moment
 * any of them gains a member — which is exactly when a shared badge would otherwise start
 * rendering an unstyled status.
 *
 * **Not a ladder, in any of the three.** FR-163 writes the objective lifecycle with
 * arrows, but `VALID_OBJECTIVE_TRANSITIONS` permits `review → {approved, certified}`. The
 * peril structure's is likewise not a sequence: `draft → review` is not an edge at all, since
 * FR-190 makes the reconciliation the evidence an approver reads, so a structure reaching
 * review without one "is not a state to refuse later — it is a state with no edge into it".
 * Nothing here or in any caller may present these as steps.
 */
import type { ObjectiveStatus } from "@/api/objectives";
import type { MetricStatus } from "@/api/metrics";
import type { PerilStructureStatus } from "@/api/perils";

type ArtifactStatus = ObjectiveStatus | MetricStatus | PerilStructureStatus;

defineProps<{ status: ArtifactStatus }>();

const TONE: Record<ArtifactStatus, string> = {
  draft: "bg-slate-100 text-slate-700",
  certified: "bg-sky-100 text-sky-800",
  reconciled: "bg-sky-100 text-sky-800",
  review: "bg-amber-100 text-amber-900",
  approved: "bg-emerald-100 text-emerald-800",
  deprecated: "bg-slate-200 text-slate-500",
  superseded: "bg-slate-200 text-slate-500",
  archived: "bg-slate-200 text-slate-500",
};
</script>

<template>
  <span :class="['rounded px-2 py-0.5 text-xs font-medium', TONE[status]]">{{ status }}</span>
</template>
