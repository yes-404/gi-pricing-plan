<script setup lang="ts">
/**
 * `02` §5.3's Objective certificate, `/objectives/:id/certificate`.
 *
 * **FR-152, as amended 2026-08-25: a `violated` check is a finding, not a failure.** This
 * view is the one FR-24 named as carrying that obligation, and the amendment is what
 * discharged it. Concretely: `violated` is never styled, labelled, grouped or ordered as a
 * failure; the certificate reads as blocked only when `overall` is `failed`; and where a check
 * is `violated` the declared hessian clipping strategy is shown beside it, because the finding
 * without the strategy is the half an Approver cannot act on.
 *
 * **Checks render in the artifact's own order.** Not sorted by status — grouping the findings
 * together would be the "order … as a failure" limb of the amendment, and §4.7's battery has a
 * fixed order a reader can follow.
 *
 * **Nine checks, always** (FR-158). A payload carrying fewer is a failure of the run, not
 * a smaller certificate, so the count is stated rather than quietly rendered.
 *
 * **No convexity heatmap.** The §5.3 cell names one; `CertificateCheck` is name/status/detail
 * and `SamplingSpec` carries only grid parameters, so there are no per-point hessians to plot
 * at any depth. Under FR-24 that cell binds nothing beyond the presentation rule above, and
 * under OQ-587's floor rule a heatmap would be a new requirement plus a contract change.
 */
import { computed, onMounted, ref } from "vue";

import {
  getObjective,
  getObjectiveCertificate,
  type CustomObjective,
  type ObjectiveCertificate,
} from "@/api/objectives";
import { ProblemError } from "@/api/problem";
import CheckStatusBadge from "@/components/CheckStatusBadge.vue";

const props = defineProps<{ id: string }>();

/** §4.7's battery size, held to by `battery_is_exactly` (FR-158). */
const EXPECTED_CHECKS = 9;

const objective = ref<CustomObjective | undefined>(undefined);
const certificate = ref<ObjectiveCertificate | undefined>(undefined);
const uncertified = ref(false);
const failure = ref<string | undefined>(undefined);

const OVERALL_LABEL = {
  certified: "Certified",
  certified_with_findings: "Certified with findings",
  failed: "Certification failed",
} as const;

/** True where any check is `violated` — which is what makes the strategy worth showing. */
const hasViolation = computed(() =>
  (certificate.value?.result.checks ?? []).some((check) => check.status === "violated"),
);

onMounted(async () => {
  try {
    objective.value = await getObjective(props.id);
  } catch (error) {
    failure.value = error instanceof Error ? error.message : String(error);
    return;
  }
  try {
    certificate.value = await getObjectiveCertificate(props.id);
  } catch (error) {
    // A `draft` objective legitimately has no certificate, and `load_certificate` raises
    // `NOT_FOUND` for it. **Branched on the code, not on the error type** — several codes
    // share 404 and a 403 rendered as "not certified yet" would be a false statement about
    // the artifact rather than about the caller's permissions.
    if (error instanceof ProblemError && error.code === "NOT_FOUND") uncertified.value = true;
    else if (error instanceof ProblemError) {
      failure.value = error.problem.detail ?? error.problem.title;
    } else failure.value = error instanceof Error ? error.message : String(error);
  }
});
</script>

<template>
  <section class="p-6">
    <h1 class="mb-1 text-xl font-semibold">
      Objective certificate
      <span
        v-if="objective"
        class="font-normal text-slate-500"
      >
        — {{ objective.slug }} v{{ objective.version }}
      </span>
    </h1>

    <p
      v-if="failure"
      class="text-sm text-rose-800"
    >
      {{ failure }}
    </p>

    <p
      v-else-if="uncertified"
      class="text-sm text-slate-600"
    >
      This objective has not been certified yet. Certification produces the evidence an Approver
      reads; until it runs there is no certificate to show.
    </p>

    <div v-else-if="certificate">
      <p class="mb-4 text-sm">
        <strong>{{ OVERALL_LABEL[certificate.result.overall] }}</strong>
        <span class="text-slate-500">
          — {{ certificate.result.checks.length }} of the {{ EXPECTED_CHECKS }} checks §4.7
          requires
        </span>
      </p>

      <!-- FR-152 as amended: the strategy sits beside the findings, because a finding
           without the declared strategy is the half an Approver cannot act on. -->
      <p
        v-if="hasViolation && objective?.hessian_strategy"
        class="mb-4 text-sm text-slate-600"
      >
        Declared hessian clipping strategy:
        <code>{{ objective.hessian_strategy }}</code>. A non-convex objective is certified with
        findings and needs an additional Approver; it is not refused.
      </p>

      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-slate-500">
            <th class="py-1">
              Check
            </th>
            <th>Result</th>
            <th>Detail</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="check in certificate.result.checks"
            :key="check.name"
            class="border-t border-slate-200"
          >
            <td class="py-1">
              {{ check.name }}
            </td>
            <td><CheckStatusBadge :status="check.status" /></td>
            <td>{{ check.detail }}</td>
          </tr>
        </tbody>
      </table>

      <p class="mt-4 text-xs text-slate-500">
        Sampled over {{ certificate.result.sampling.n_points }} points, seed
        {{ certificate.result.sampling.seed }}. A convexity share is only meaningful alongside
        the grid it was measured on (§4.7).
      </p>
    </div>
  </section>
</template>
