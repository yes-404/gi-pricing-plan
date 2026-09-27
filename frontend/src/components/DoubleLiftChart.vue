<script setup lang="ts">
import { BarChart, LineChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { DoubleLift } from "@/api/comparisons";
import ChartFigure from "@/components/ChartFigure.vue";

use([BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{ series: DoubleLift }>();

/**
 * Bins in the artifact's own order. `02` §4.11 orders them by the **ratio** of the two
 * predictions, which is what makes the chart answer "where the models disagree, which one is
 * right?"; re-sorting by either prediction answers the weaker question instead.
 */
const bins = computed(() => props.series.bins);

const labels = computed(() => bins.value.map((b) => String(b.bin)));

/**
 * `exposure_years` is a `DecimalStr` — exact decimal carried as a string, so a float never
 * silently rounds it. Converting it here is safe because **exposure-years denominates
 * exposure and not money**, which is FR-10's own test as amended 2026-08-24: "what a
 * quantity denominates, not how it was computed". Being a diagnostic read is not what makes
 * it safe — the same amendment says a quantity that denominates money stays integer minor
 * units "wherever it appears: inside a diagnostic payload" included.
 *
 * It is also nullable, and a bar chart with holes in it reads as zero exposure rather than as
 * unknown exposure, so the whole series is omitted unless every bin has one. The table below
 * obeys the same all-or-nothing rule, which is why the predicate is written once here and
 * both readings derive from it: a chart that plotted exposure while the table dropped the
 * column would be two different claims about the same artifact.
 */
const exposureText = computed(() => {
  const raw = bins.value.map((b) => b.exposure_years);
  return raw.every((v) => typeof v === "string") ? raw : null;
});

const exposure = computed(() => exposureText.value?.map((v) => Number(v)) ?? null);

const option = computed(() => ({
  tooltip: { trigger: "axis" as const },
  legend: { bottom: 0 },
  grid: { left: 56, right: 56, top: 16, bottom: 56 },
  xAxis: {
    type: "category" as const,
    data: labels.value,
    name: "Bin (by prediction ratio)",
    nameLocation: "middle" as const,
    nameGap: 30,
  },
  yAxis: [
    { type: "value" as const, name: "Rate", position: "left" as const },
    ...(exposure.value
      ? [
          {
            type: "value" as const,
            name: "Exposure",
            position: "right" as const,
            splitLine: { show: false },
          },
        ]
      : []),
  ],
  series: [
    // Grey is reserved for exposure across every chart in this app (HistogramChart.vue).
    ...(exposure.value
      ? [
          {
            name: "Exposure",
            type: "bar" as const,
            yAxisIndex: 1,
            data: exposure.value,
            itemStyle: { color: "#cbd5e1" },
          },
        ]
      : []),
    // Actual is the reference truth, so it takes the neutral darkest and a solid line. The
    // three lines differ by line type as well as by hue, which is what NFR-463's WCAG
    // obligation needs.
    {
      name: "Actual",
      type: "line" as const,
      data: bins.value.map((b) => b.actual),
      itemStyle: { color: "#0f172a" },
      lineStyle: { color: "#0f172a", type: "solid" as const, width: 2 },
    },
    {
      name: "Baseline predicted",
      type: "line" as const,
      data: bins.value.map((b) => b.baseline_predicted),
      itemStyle: { color: "#0f766e" },
      lineStyle: { color: "#0f766e", type: "dashed" as const, width: 2 },
    },
    {
      name: "Challenger predicted",
      type: "line" as const,
      data: bins.value.map((b) => b.challenger_predicted),
      itemStyle: { color: "#b45309" },
      lineStyle: { color: "#b45309", type: "dotted" as const, width: 2 },
    },
  ],
}));

/**
 * The chart's accessible equivalent (NFR-463). Each plotted series gets its own column,
 * named exactly as the legend names it, so a reader moving between the two is not asked to
 * match "Baseline predicted" against some shortened heading.
 *
 * `rows` is carried by the artifact and plotted by nothing, and it is tabled anyway. The
 * chart can leave volume implicit because a reader sees where the exposure bars are tall;
 * the table cannot, and `exposure_years` is all-or-nothing, so when it is absent a
 * `rows`-less table would say nothing at all about how much of the book each bin holds —
 * which is what decides whether a divergence between the two models matters. This is the
 * superset the retrofit is licensed to table, not a smaller thing than the chart shows.
 */
const columns = computed(() => [
  "Bin (by prediction ratio)",
  "Rows",
  ...(exposureText.value ? ["Exposure"] : []),
  "Actual",
  "Baseline predicted",
  "Challenger predicted",
]);

/**
 * Exposure reaches the table as the exact decimal **string** it was recorded as (FR-10).
 * The chart widens it because a coordinate is a float64 either way and nothing computes with
 * it; a table cell has no such excuse, and a trailing zero lost there is a value the reader
 * cannot tell apart from a rounded one. `AeByFactorChart` set this precedent.
 */
const rows = computed(() =>
  bins.value.map((b, i) => [
    String(b.bin),
    b.rows,
    ...(exposureText.value ? [exposureText.value[i] ?? null] : []),
    b.actual,
    b.baseline_predicted,
    b.challenger_predicted,
  ]),
);
</script>

<template>
  <ChartFigure
    :title="`Double lift: baseline against ${series.challenger_ref}`"
    :caption="`${series.weighting}-weighted, binned by the ratio of the two predictions.`"
    :columns="columns"
    :rows="rows"
  >
    <VChart
      class="h-80 w-full"
      :option="option"
      autoresize
    />
  </ChartFigure>
</template>
