<script setup lang="ts">
/**
 * FR-190's verdict: the modelled burning cost reconciles to the observed one within a
 * declared tolerance, computed on the holdout.
 *
 * **No absolute amount and no currency symbol, deliberately.** The two burning-cost fields are
 * `MoneyMinor` integers, and formatting minor units needs a currency this view cannot reach:
 * `Reconciliation` carries a `dataset_version_id`, and OQ-551 records that a view holding a
 * dataset *version* id has no route to one — `DatasetVersion` carries no currency and
 * `/datasets/{dataset_id}` is PATCH-only. This panel is that open question's fourth view.
 *
 * Nothing requirement-backed is lost by omitting them. `ratio`, `tolerance` and the derived
 * `status` are **dimensionless**, and they are exactly what FR-190 makes the requirement.
 * FR-128's per-peril breakdown is preserved as each peril's **share of the modelled
 * total**, also dimensionless. The precedents are W6b-5b, which omitted the incurred column
 * rather than guess, and W6b-9, which made `OneWayChart`'s currency prop required so a
 * hardcoded `"GBP"` could not propagate. The absolute figures return when OQ-551 is decided.
 *
 * **`ratio` and `status` are read, never recomputed.** Both are `computed_field`s on the wire —
 * derived server-side, and `Reconciliation`'s own validator discards them on the way in. A
 * second client-side computation of a persisted verdict is the "two statements of one fact
 * disagree eventually" defect the contract exists to prevent.
 *
 * **`ratio` and `tolerance` are `DecimalStr` — strings, never floats.** They are rendered as
 * they arrived. The share below is integer arithmetic on the minor values, which is exact.
 */
import { computed } from "vue";

import type { components } from "@/api/generated/schema";

type Reconciliation = components["schemas"]["Reconciliation"];

const props = defineProps<{ reconciliation: Reconciliation }>();

/**
 * Each peril's share of the modelled total, as a percentage.
 *
 * Dimensionless, so it carries FR-128's breakdown without asserting a denomination. A
 * zero total yields `null` rather than a division by zero — a structure modelling nothing has
 * no shares, which is a different statement from "0%".
 */
const shares = computed(() => {
  const total = props.reconciliation.modelled_burning_cost;
  return props.reconciliation.perils.map((peril) => ({
    peril: peril.peril,
    kind: peril.large_loss_kind,
    share: total > 0 ? Math.round((peril.modelled_burning_cost / total) * 100) : null,
  }));
});
</script>

<template>
  <section class="mt-6">
    <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
      Reconciliation
    </h2>

    <p class="mt-2 text-sm">
      <strong>{{ reconciliation.status }}</strong>
      — ratio {{ reconciliation.ratio }} against a declared tolerance of
      {{ reconciliation.tolerance }}, computed on the
      <strong>{{ reconciliation.part }}</strong> part.
    </p>

    <!-- FR-128: the per-peril breakdown, as share of the modelled total. -->
    <table class="mt-3 w-full text-left text-sm">
      <caption class="sr-only">
        Modelled burning cost by peril, as a share of the total
      </caption>
      <thead class="border-b border-slate-200 text-xs uppercase text-slate-500">
        <tr>
          <th
            scope="col"
            class="py-1 font-medium"
          >
            Peril
          </th>
          <th
            scope="col"
            class="py-1 font-medium"
          >
            Large loss
          </th>
          <th
            scope="col"
            class="py-1 font-medium"
          >
            Share of modelled
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in shares"
          :key="row.peril"
          class="border-b border-slate-100"
        >
          <td class="py-1">
            {{ row.peril }}
          </td>
          <td class="py-1">
            {{ row.kind }}
          </td>
          <td class="py-1 tabular-nums">
            {{ row.share === null ? "—" : `${row.share}%` }}
          </td>
        </tr>
      </tbody>
    </table>

    <!--
      Says why the absolute figures are absent **without naming a denomination**. OQ-538 is
      open on whether burning cost is money at all — its recommendation is that it is a
      statistic and the `_minor` suffix is the defect — so a label reading "minor units" would
      take a side the repository has not taken. `01`'s `validate.py` shipped exactly that
      string about a statistic and it took a separate sweep to find.
    -->
    <p class="mt-2 text-xs text-slate-500">
      Shares rather than absolute figures: this view has no route to the workspace currency, so
      an amount shown here could not say what it was denominated in.
    </p>
  </section>
</template>
