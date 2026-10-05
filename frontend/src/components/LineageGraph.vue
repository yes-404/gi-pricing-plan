<script setup lang="ts">
import { computed } from "vue";
import { use } from "echarts/core";
import { GraphChart } from "echarts/charts";
import { TooltipComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import VChart from "vue-echarts";

import type { DatasetLineage } from "@/api/datasets";
import type { Column } from "@/chart-table";
import ChartFigure from "./ChartFigure.vue";

use([GraphChart, TooltipComponent, CanvasRenderer]);

const props = defineProps<{
  lineage: DatasetLineage;
  /** The queried version's number — the payload carries ids, not numbers. */
  version: number;
}>();

type GraphNode = { id: string; name: string; category: number; x: number; y: number };

const versionNode = computed<GraphNode>(() => ({
  id: props.lineage.version_id,
  name: `v${props.version}`,
  category: 0,
  x: 50,
  y: 60,
}));

const parentNode = computed<GraphNode | null>(() => {
  const builtFrom = props.lineage.built_from;
  if (builtFrom === null) return null;
  return {
    id: builtFrom.parent_version_id,
    name: builtFrom.parent_version_id.slice(0, 8),
    category: 0,
    x: 50,
    y: 0,
  };
});

const childNodes = computed<GraphNode[]>(() => {
  const derived = props.lineage.depends_on_this.derived_versions ?? [];
  return derived.map((child, i) => ({
    id: child.version_id,
    name: `v${child.version}`,
    category: 0,
    x: 50 + (i - (derived.length - 1) / 2) * 90,
    y: 120,
  }));
});

const modelNodes = computed<GraphNode[]>(() => {
  const models = props.lineage.depends_on_this.models ?? [];
  return models.map((model, i) => ({
    id: model.model_id,
    name: model.slug,
    category: 1,
    x: 50 + (i - (models.length - 1) / 2) * 120,
    y: 180,
  }));
});

const nodes = computed<GraphNode[]>(() => {
  const list: GraphNode[] = [versionNode.value];
  if (parentNode.value) list.push(parentNode.value);
  list.push(...childNodes.value, ...modelNodes.value);
  return list;
});

const links = computed(() => {
  const list: { source: string; target: string; symbol: string[] }[] = [];
  if (parentNode.value) {
    list.push({ source: parentNode.value.id, target: versionNode.value.id, symbol: ["none", "arrow"] });
  }
  for (const child of childNodes.value) {
    list.push({ source: versionNode.value.id, target: child.id, symbol: ["none", "arrow"] });
  }
  for (const model of modelNodes.value) {
    list.push({ source: versionNode.value.id, target: model.id, symbol: ["none", "arrow"] });
  }
  return list;
});

const option = computed(() => ({
  tooltip: { trigger: "item" as const },
  series: [
    {
      type: "graph" as const,
      layout: "none",
      data: nodes.value,
      links: links.value,
      categories: [{ name: "version" }, { name: "model" }],
      roam: false,
      label: { show: true, position: "bottom" as const },
      lineStyle: { color: "#94a3b8" },
      itemStyle: { color: "#0284c7" },
      emphasis: { focus: "adjacency" as const },
    },
  ],
}));

/**
 * One row of the lineage table. Component-local: no backend shape describes it, since the
 * table flattens the parent, this version, its derived versions and its models into one list.
 */
interface LineageRow {
  kind: string;
  name: string;
  operation: string | null;
  status: string | null;
}

const columns: readonly Column<LineageRow>[] = [
  { key: "kind", label: "Kind", value: (r) => r.kind },
  { key: "name", label: "Name", value: (r) => r.name },
  { key: "operation", label: "Operation", value: (r) => r.operation },
  { key: "status", label: "Status", value: (r) => r.status },
];

const rows = computed<readonly LineageRow[]>(() => {
  const list: LineageRow[] = [];
  if (parentNode.value) {
    list.push({
      kind: "Built from",
      name: parentNode.value.name,
      operation: props.lineage.built_from?.operation ?? null,
      status: null,
    });
  }
  list.push({ kind: "This version", name: versionNode.value.name, operation: null, status: null });
  for (const child of props.lineage.depends_on_this.derived_versions ?? []) {
    list.push({ kind: "Derived version", name: `v${child.version}`, operation: child.operation, status: null });
  }
  for (const model of props.lineage.depends_on_this.models ?? []) {
    list.push({ kind: "Model", name: model.slug, operation: null, status: model.status });
  }
  return list;
});
</script>

<template>
  <ChartFigure
    title="Lineage"
    caption="What this version was built from, and what was built from it."
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
