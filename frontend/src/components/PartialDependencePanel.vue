<script setup lang="ts">
import { LineChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import VChart from "vue-echarts";

import type { PartialDependence } from "@/api/diagnostics";
import ChartFigure from "@/components/ChartFigure.vue";

use([LineChart, GridComponent, TooltipComponent, CanvasRenderer]);

defineProps<{ partialDependence: readonly PartialDependence[] }>();

/**
 * Partial dependence for the declared factors (FR-MODEL-52), one figure per factor.
 *
 * Unpartitioned: a curve is the fitted response held at a value, a property of the fit rather
 * than a measurement against a population of rows.
 *
 * **The omissions are rendered, not skipped.** `PartialDependenceOmissionReason` exists so a
 * factor with no curve is named with its reason; a panel that dropped those factors would
 * report a gap as an absence, and the reader could not tell a factor the sweep never reached
 * from one it reached and found nothing in.
 */
function option(entry: PartialDependence) {
  return {
    tooltip: { trigger: "axis" as const },
    grid: { left: 60, right: 30, top: 20, bottom: 60 },
    xAxis: {
      type: "category" as const,
      data: entry.points.map((point) => point.value),
      axisLabel: { rotate: 45 },
    },
    yAxis: { type: "value" as const, name: "Mean prediction", scale: true },
    series: [
      {
        name: entry.factor,
        type: "line" as const,
        data: entry.points.map((point) => point.mean_prediction),
        lineStyle: { type: "solid" as const, width: 2 },
      },
    ],
  };
}

function rows(entry: PartialDependence) {
  return entry.points.map((point) => [point.value, point.mean_prediction, point.exposure_share]);
}

/**
 * FR-MODEL-118's reasons, in words. The enum value is an identifier and says nothing to a
 * reader; an unrecognised one is passed through rather than mapped to a default, because a
 * new reason shown under the wrong English is worse than one shown under its own name.
 *
 * `levels` counts what the sweep **did not visit** — the contract calls it "levels present in
 * the data that the sweep did not visit", and its validator "the levels it dropped". So the
 * sentence says skipped rather than total: the same number under the other reading would tell
 * a reader the factor is small when it is the omission that is large.
 */
function explain(omission: NonNullable<PartialDependence["omitted"]>): string {
  if (omission.reason === "level_cap") {
    return `The categorical grid was truncated to the most-exposed levels${
      omission.levels == null ? "" : `; ${omission.levels} levels were not visited`
    }. The rest are not pooled into an "other" bar, because a level the model never saw is refused at encoding.`;
  }
  if (omission.reason === "no_source_column") {
    return "The factor sources no column of its own — an interaction, whose columns are its operands' — so there is nothing to hold at a value.";
  }
  return omission.reason;
}
</script>

<template>
  <div>
    <template
      v-for="entry in partialDependence"
      :key="entry.factor"
    >
      <ChartFigure
        v-if="entry.points.length"
        :title="entry.factor"
        caption="Mean prediction with the factor held at each value, exposure share beside it."
        :columns="['Value', 'Mean prediction', 'Exposure share']"
        :rows="rows(entry)"
      >
        <VChart
          class="h-64 w-full"
          :option="option(entry)"
          autoresize
        />
      </ChartFigure>

      <div
        v-else
        class="mt-6 rounded-md border border-slate-200 bg-slate-50 p-4 text-sm"
      >
        <h3 class="font-semibold text-slate-700">
          {{ entry.factor }}
        </h3>
        <p
          v-if="entry.omitted"
          class="mt-1 text-slate-600"
        >
          No curve. {{ explain(entry.omitted) }}
          <span v-if="entry.omitted.exposure_share != null">
            The omitted levels carry {{ entry.omitted.exposure_share }} of exposure.
          </span>
        </p>
        <p
          v-else
          class="mt-1 text-slate-600"
        >
          No curve, and the artifact records no reason.
        </p>
      </div>
    </template>
  </div>
</template>
