<script setup lang="ts">
import { computed } from "vue";

import {
  intervalClaim,
  unavailableCopy,
  type PredictedRow,
  type Uncertainty,
} from "@/api/predictions";

const props = defineProps<{ uncertainty: Uncertainty; row: PredictedRow }>();

/**
 * FR-MODEL-101 forbids `basis` on a `quantile_pair_interval` and requires `interval_models`
 * on it; FR-MODEL-98's kind is the mirror image. The generated `Uncertainty` is a flat object
 * with every field nullable, so neither rule is expressible in the type — the component
 * branches on `kind` and reads only the fields that kind is allowed to carry. A stray `basis`
 * on a quantile pair is therefore ignored rather than rendered, which matters because
 * rendering it would attach a GLM's claim to a GBM's bound.
 */
const showBasis = computed(
  () => props.uncertainty.kind === "confidence_interval_mean" && props.uncertainty.basis !== null,
);

const showIntervalModels = computed(
  () =>
    props.uncertainty.kind === "quantile_pair_interval"
    && props.uncertainty.interval_models !== null,
);

const claim = computed(() =>
  props.uncertainty.kind === "unavailable" ? null : intervalClaim(props.uncertainty.kind),
);

/**
 * `reason` is optional **and** nullable, so absence arrives two ways: `null` from the wire and
 * `undefined` from an omitted key. Normalised once here — a `!== null` test alone would let an
 * omitted key through as a reason and hand `undefined` to an exhaustive switch.
 */
const refusal = computed(() => {
  const reason = props.uncertainty.reason ?? null;
  return props.uncertainty.kind === "unavailable" && reason !== null
    ? unavailableCopy(reason)
    : null;
});

/**
 * FR-MODEL-99: `unpenalised_information_matrix` means the matrix was computed as though the
 * fit were unpenalised, so the interval is **wider** than the shrunk estimate warrants. That
 * direction is the whole content of the caveat — an actuary who reads it as "narrower" draws
 * the opposite conclusion about precision.
 */
const basisCopy = computed(() =>
  props.uncertainty.basis === "unpenalised_information_matrix"
    ? "unpenalised information matrix — this fit is penalised, so the interval is wider than "
      + "the shrunk estimate warrants, which is conservative rather than wrong"
    : "information matrix",
);

const percent = computed(() =>
  props.uncertainty.level === null || props.uncertainty.level === undefined
    ? null
    : `${(props.uncertainty.level * 100).toFixed(0)}%`,
);
</script>

<template>
  <section class="mt-4 rounded-md border border-slate-200 p-4">
    <p
      class="text-2xl font-semibold"
      data-testid="expected"
    >
      {{ row.expected }}
    </p>
    <p class="text-xs text-slate-500">
      Expected value
    </p>

    <template v-if="claim !== null && row.lower !== null && row.upper !== null">
      <p
        class="mt-3 font-mono text-sm"
        data-testid="interval"
      >
        {{ row.lower }} &ndash; {{ row.upper }}
      </p>
      <p class="text-xs text-slate-600">
        {{ percent === null ? "Interval" : `${percent} interval` }} for {{ claim }}.
      </p>
      <p
        v-if="showBasis"
        class="mt-1 text-xs text-slate-500"
        data-testid="uncertainty-basis"
      >
        Computed on the {{ basisCopy }}.
      </p>
      <!-- FR-MODEL-78: a bound is a Model in its own right, at a declared alpha. Naming both
           is what lets a reader check the pair is the one they think it is. -->
      <p
        v-if="showIntervalModels && uncertainty.interval_models"
        class="mt-1 text-xs text-slate-500"
        data-testid="interval-models"
      >
        From paired quantile models at alpha {{ uncertainty.interval_models.lower_alpha }} and
        {{ uncertainty.interval_models.upper_alpha }}.
      </p>
    </template>

    <div
      v-else-if="uncertainty.kind === 'unavailable'"
      class="mt-3 rounded bg-slate-50 p-3"
    >
      <template v-if="refusal">
        <p class="text-sm font-medium">
          {{ refusal.headline }}
        </p>
        <p class="mt-1 text-xs text-slate-600">
          {{ refusal.detail }}
        </p>
      </template>
      <!-- FR-MODEL-63 requires the reason, so a null one is a breach on the server's side.
           Reported as such: an empty panel would read as "the page forgot". -->
      <p
        v-else
        class="text-sm text-amber-900"
      >
        No interval, and the response carried no reason for it. FR-MODEL-63 requires one.
      </p>
    </div>
  </section>
</template>
