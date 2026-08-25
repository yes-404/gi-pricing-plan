<script setup lang="ts">
import { BarChart, CustomChart, LineChart } from "echarts/charts";
import {
  DataZoomComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,
} from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { OneWaySummary } from "@/api/profiles";
import { formatDecimalString, formatMinor } from "@/api/versions";
import ChartFigure from "@/components/ChartFigure.vue";

use([BarChart, LineChart, CustomChart, GridComponent, TooltipComponent, LegendComponent,
     DataZoomComponent, CanvasRenderer]);

const props = defineProps<{
  summary: OneWaySummary;
  /**
   * The workspace currency the incurred amounts are denominated in. Required, with no
   * default: `claim_amount_minor` is minor units *of the workspace currency*, and a
   * component that guessed "GBP" would render euro amounts with a pound sign — a wrong
   * number that looks like a right one. A caller that does not know the currency has no
   * business formatting the amount, so the type says so.
   */
  currency: string;
}>();

const rows = computed(() => props.summary.rows ?? []);
const levels = computed(() => rows.value.map((row) => row.level));

/**
 * Exposure as bars, frequency as a line, on two axes.
 *
 * The pairing is the point of a one-way: a level with a high frequency and almost no
 * exposure is noise, and the chart has to make that visible at a glance rather than invite
 * an actuary to rate on four policies.
 *
 * `exposure_years` is an exact decimal **string** (FR-OVR-7). `Number()` here is
 * deliberate and safe: a chart coordinate is a float64 either way, and the value being
 * plotted is not the value being stored. Nothing computes with it.
 */
const option = computed(() => ({
  tooltip: { trigger: "axis" as const },
  legend: { data: ["Exposure", "Frequency"], bottom: 0 },
  grid: { left: 60, right: 60, top: 20, bottom: 50 },
  xAxis: { type: "category" as const, data: levels.value, axisLabel: { rotate: 45 } },
  yAxis: [
    { type: "value" as const, name: "Exposure", position: "left" as const },
    { type: "value" as const, name: "Frequency", position: "right" as const },
  ],
  series: [
    {
      name: "Exposure",
      type: "bar" as const,
      data: rows.value.map((row) => Number(row.exposure_years)),
      itemStyle: { color: "#cbd5e1" },
      yAxisIndex: 0,
    },
    {
      name: "Frequency",
      type: "line" as const,
      data: rows.value.map((row) => row.frequency),
      yAxisIndex: 1,
      symbolSize: 6,
      lineStyle: { color: "#0f766e" },
      itemStyle: { color: "#0f766e" },
    },
    {
      // The exact Poisson interval (FR-DATA-26), drawn as a whisker per level. A
      // frequency without one invites a decision the count cannot support — nine claims
      // in a young-driver band look either significant or like noise depending entirely
      // on this.
      name: "Frequency CI",
      type: "custom" as const,
      yAxisIndex: 1,
      silent: true,
      renderItem: renderInterval,
      encode: { x: 0, y: [1, 2] },
      data: rows.value.map((row, index) => [
        index,
        row.frequency_ci?.[0] ?? null,
        row.frequency_ci?.[1] ?? null,
      ]),
    },
  ],
}));

function renderInterval(params: unknown, api: unknown): unknown {
  const a = api as {
    value: (index: number) => number;
    coord: (point: [number, number]) => [number, number];
    size: (value: [number, number]) => [number, number];
  };
  const low = a.value(1);
  const high = a.value(2);
  if (low == null || high == null || Number.isNaN(low)) return undefined;

  const [x, yLow] = a.coord([a.value(0), low]);
  const [, yHigh] = a.coord([a.value(0), high]);
  const halfWidth = Math.max(a.size([1, 0])[0] * 0.15, 2);
  const style = { stroke: "#0f766e", lineWidth: 1, opacity: 0.7 };

  return {
    type: "group",
    children: [
      { type: "line", shape: { x1: x, y1: yLow, x2: x, y2: yHigh }, style },
      { type: "line", shape: { x1: x - halfWidth, y1: yLow, x2: x + halfWidth, y2: yLow }, style },
      { type: "line", shape: { x1: x - halfWidth, y1: yHigh, x2: x + halfWidth, y2: yHigh }, style },
    ],
  };
}

/**
 * The chart's accessible equivalent (NFR-OVR-10), and until now the only chart on the
 * Profile page that had one — hand-written in `ProfileView`, beside the chart rather than
 * bound to it, and therefore attached to that one call site instead of to the component
 * that draws the canvas. It moves here so that any view rendering a one-way gets the table
 * with it.
 *
 * It carries two columns the canvas does not draw as a series, which is what makes it a
 * superset rather than a transcription:
 *
 * - **Frequency CI** *is* plotted, as the whiskers `renderInterval` draws, and a whisker is
 *   the least transcribable mark on the chart: it has no legend entry and no tooltip. It is
 *   in the table for exactly the reason the series comment gives — a frequency without its
 *   interval invites a decision the claim count cannot support.
 * - **Severity CI** is plotted by nothing and is tabled anyway. Tabling the frequency's
 *   interval and withholding the severity's would tell the reader that the frequency needs
 *   one and the mean severity does not, which is not what FR-DATA-26 says; severity from
 *   nine claims is the less stable of the two, not the more.
 */
const columns = [
  "Level",
  "Exposure",
  "Claims",
  "Incurred",
  "Frequency",
  "Frequency CI",
  "Severity",
  "Severity CI",
  "Burning cost",
];

/** An interval as one cell. `—` when it is absent, which below two claims it always is. */
function interval(ci: readonly [number, number] | null | undefined, digits: number, scale = 1) {
  if (ci == null) return null;
  return `${(ci[0] / scale).toFixed(digits)}–${(ci[1] / scale).toFixed(digits)}`;
}

/**
 * `mean_severity`, `mean_burning_cost` and `severity_ci` are **float ratios**, not amounts:
 * amount ÷ claims and amount ÷ exposure. Formatting them as currency would imply an
 * exactness they do not have, so they are shown as the statistics they are. Still expressed
 * in minor units — only the name changed (FR-DATA-46) — so the `/ 100` scaling stays.
 *
 * `severity_ci` shares that scale because it is computed from the same `claim_amount_minor`
 * sum `mean_severity` is (`pricing_core.data.profile._one_way_row`), so it is divided the
 * same way rather than on the assumption that an interval matches its statistic.
 */
const tableRows = computed(() =>
  rows.value.map((row) => [
    row.level,
    formatDecimalString(row.exposure_years),
    row.claim_count.toLocaleString(),
    formatMinor(row.claim_amount_minor, props.currency),
    row.frequency?.toFixed(4) ?? null,
    interval(row.frequency_ci, 4),
    row.mean_severity == null ? null : (row.mean_severity / 100).toFixed(2),
    interval(row.severity_ci, 2, 100),
    row.mean_burning_cost == null ? null : (row.mean_burning_cost / 100).toFixed(2),
  ]),
);
</script>

<template>
  <ChartFigure
    v-if="rows.length"
    :title="`One-way: ${summary.column}`"
    caption="Exposure and claim frequency by level, with intervals on the frequency and the
             mean severity."
    :columns="columns"
    :rows="tableRows"
  >
    <VChart
      class="h-80 w-full"
      :option="option"
      autoresize
    />
  </ChartFigure>
  <p
    v-else
    class="text-sm text-slate-500"
  >
    This column has no stored one-way.
  </p>
</template>
