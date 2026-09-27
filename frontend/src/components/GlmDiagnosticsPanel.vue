<script setup lang="ts">
import { computed } from "vue";

import type { GlmDiagnostics } from "@/api/diagnostics";

const props = defineProps<{ glm: GlmDiagnostics }>();

/**
 * GLM-specific diagnostics (FR-172).
 *
 * None of it is partitioned: `GlmDiagnostics` declares neither `train` nor `holdout`, because
 * a deviance, a variance inflation factor and a type-III test are properties of one fit
 * rather than measurements against a population of rows (FR-183, as scoped 2026-08-24).
 *
 * `aic` and `bic` are nullable and rendered as an em dash when absent. The contract says why:
 * a family with no closed-form likelihood this platform evaluates — Tweedie's density needs a
 * series expansion — has no AIC to record. A zero there would read as a perfect likelihood.
 */
const statistics = computed(() => [
  { name: "Deviance", value: props.glm.deviance },
  { name: "Null deviance", value: props.glm.null_deviance },
  { name: "AIC", value: props.glm.aic },
  { name: "BIC", value: props.glm.bic },
  { name: "Dispersion", value: props.glm.dispersion },
  { name: "Degrees of freedom", value: props.glm.degrees_of_freedom },
]);

/**
 * `?? {}` because `vif` is **optional** in the generated type while `aliasing` and
 * `type_iii_tests`, which default the same way in Python, are required. The asymmetry is
 * real and comes from the schema: `Field(default_factory=dict)` emits no `default`, so
 * openapi-typescript marks the property optional, whereas `= ()` emits `default: []` and it
 * stays required. Not a shape to hand-correct — the generator is the source of truth
 * (ADR-704), so the reader absorbs it here.
 */
const vif = computed(() => Object.entries(props.glm.vif ?? {}));

/**
 * FR-173: an `aliasing` entry is the **bare name** of a collinear term, and the
 * contract says so — the field is read by a human deciding which factor to drop, and a name
 * is what they act on. The object form `{term, aliased_with, reason}` is not shipped; if this
 * view needs those fields, that is a new requirement raised at that point.
 */
const aliasing = computed(() => props.glm.aliasing);

/**
 * FR-172 also names standardised deviance and Pearson residual plots and leverage on a
 * sample. The contract carries only blob **references** for those, and no endpoint resolves
 * one — `02`'s NFR note names the owner as the slice that first stores a per-row residual
 * series, which is not this one. So the presence of a reference is reported and the series is
 * named as unavailable, rather than an empty chart frame implying a fit with no residuals.
 */
const blobs = computed(() =>
  [
    { name: "Residuals", ref: props.glm.residual_blob },
    { name: "Leverage", ref: props.glm.leverage_blob },
  ].map((blob) => ({
    ...blob,
    state: blob.ref == null ? "not recorded by this fit" : "recorded, not retrievable yet",
  })),
);
</script>

<template>
  <div>
    <table
      aria-label="GLM fit statistics"
      class="mt-2 w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Statistic
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Value
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="statistic in statistics"
          :key="statistic.name"
          class="border-b border-slate-100"
        >
          <th
            scope="row"
            class="py-1 font-normal"
          >
            {{ statistic.name }}
          </th>
          <td class="py-1 tabular-nums">
            {{ statistic.value ?? "—" }}
          </td>
        </tr>
      </tbody>
    </table>

    <!-- `type_iii_tests`, `aliasing` and `vif` all default to empty in the contract, so each
         gets a sentence rather than a header over no rows. An empty table reads as "measured,
         nothing to report"; absent is what it means. -->
    <table
      v-if="glm.type_iii_tests.length"
      aria-label="Type III deviance tests"
      class="mt-6 w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Factor
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Deviance delta
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            df
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            p-value
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="test in glm.type_iii_tests"
          :key="test.factor"
          class="border-b border-slate-100"
        >
          <th
            scope="row"
            class="py-1 font-normal"
          >
            {{ test.factor }}
          </th>
          <td class="py-1 tabular-nums">
            {{ test.deviance_delta }}
          </td>
          <td class="py-1 tabular-nums">
            {{ test.df }}
          </td>
          <td class="py-1 tabular-nums">
            {{ test.p_value }}
          </td>
        </tr>
      </tbody>
    </table>
    <p
      v-else
      class="mt-6 text-sm text-slate-500"
    >
      No type-III tests were recorded for this fit.
    </p>

    <table
      v-if="vif.length"
      aria-label="Variance inflation"
      class="mt-6 w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Term
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            VIF
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="[term, value] in vif"
          :key="term"
          class="border-b border-slate-100"
        >
          <th
            scope="row"
            class="py-1 font-normal"
          >
            {{ term }}
          </th>
          <td class="py-1 tabular-nums">
            {{ value }}
          </td>
        </tr>
      </tbody>
    </table>
    <p
      v-else
      class="mt-6 text-sm text-slate-500"
    >
      No variance inflation factors were recorded for this fit.
    </p>

    <div class="mt-6">
      <h3 class="text-sm font-semibold text-slate-700">
        Aliased terms
      </h3>
      <ul
        v-if="aliasing.length"
        class="mt-1 list-inside list-disc text-sm"
      >
        <li
          v-for="term in aliasing"
          :key="term"
          class="font-mono text-xs"
        >
          {{ term }}
        </li>
      </ul>
      <p
        v-else
        class="mt-1 text-sm text-slate-500"
      >
        No terms were aliased — the design matrix was full rank.
      </p>
    </div>

    <div class="mt-6">
      <h3 class="text-sm font-semibold text-slate-700">
        Residual and leverage series
      </h3>
      <ul class="mt-1 text-sm text-slate-500">
        <li
          v-for="blob in blobs"
          :key="blob.name"
        >
          {{ blob.name }}: {{ blob.state }}.
        </li>
      </ul>
      <p class="mt-1 text-xs text-slate-500">
        FR-172 names residual and leverage plots. The artifact carries a reference rather
        than the series, and no read resolves one yet, so they are named here rather than
        drawn empty.
      </p>
    </div>
  </div>
</template>
