<script setup lang="ts">
/**
 * The canvas, the keyboard navigator, the per-type inspector and the add-step menu (03 §5.3).
 * Edges are drawn from `consumes`/`produces` and edited in the inspector, never on the canvas:
 * a drag-to-connect needs the validity check that is S3's (RL-1474), and building it here
 * would define the check twice. Imports its CSS here so it rides in the lazy `vueflow` chunk.
 */
import "@vue-flow/core/dist/style.css";
import "@vue-flow/core/dist/theme-default.css";

import { VueFlow, useVueFlow } from "@vue-flow/core";
import { computed, ref } from "vue";

import type {
  AlgorithmDiff,
  ModelReferenceMode,
  RatingAlgorithmDraft,
  RatingStep,
} from "@/api/ratingAlgorithms";
import type { SubGraphRef } from "@/api/subGraphs";

import { edgesOf, layout } from "./graph";
import DiffOverlay from "./DiffOverlay.vue";
import GraphIssues from "./GraphIssues.vue";
import MountInspector from "./MountInspector.vue";
import MountNode from "./MountNode.vue";
import NodeNavigator from "./NodeNavigator.vue";
import StepInspector from "./StepInspector.vue";
import StepNode from "./StepNode.vue";
import { useGraphValidation } from "./useGraphValidation";

const props = withDefaults(
  defineProps<{
    draft: RatingAlgorithmDraft;
    versionMode: ModelReferenceMode;
    rateTablePins: string[];
    /** The Rating Version's `pins.sub_graphs`: the only versions a mount may name (RL-1835 (iii) 1). */
    subGraphPins?: string[];
  }>(),
  { subGraphPins: () => [] },
);

const emit = defineEmits<{ "update:draft": [draft: RatingAlgorithmDraft] }>();

// Pinned to the generated union: a step type added server-side fails type-check here.
const STEP_TYPES = [
  "input",
  "lookup",
  "table",
  "expression",
  "model_call",
  "constraint",
  "output",
] as const satisfies readonly RatingStep["type"][];

const selected = ref<string | null>(null);
const added = ref(new Set<string>());
const nextType = ref<(typeof STEP_TYPES)[number]>("expression");

const { issues, pending, byStep, graphLevel } = useGraphValidation(() => props.draft);
const issueCounts = computed(
  () => new Map([...byStep.value].map(([id, list]) => [id, list.length] as const)),
);
const issueSummary = computed(() => {
  const n = issues.value.length;
  return `${n} ${n === 1 ? "issue" : "issues"}`;
});

const diff = ref<AlgorithmDiff | null>(null);
const diffMarks = computed(() => {
  const marks = new Map<string, "added" | "changed">();
  if (diff.value === null) return marks;
  for (const id of (diff.value.added_steps ?? [])) marks.set(id, "added");
  for (const c of (diff.value.changed_steps ?? [])) marks.set(c.step_id, "changed");
  for (const r of (diff.value.repointed_tables ?? [])) marks.set(r.step_id, "changed");
  for (const m of (diff.value.sub_graph_mounts ?? [])) {
    marks.set(m.mount_point, m.before == null ? "added" : "changed");
  }
  return marks;
});

const steps = computed(() => props.draft.steps);
const mounts = computed(() => props.draft.sub_graphs ?? []);
const current = computed(() => steps.value.find((s) => s.step_id === selected.value));
const currentMount = computed(() => mounts.value.find((m) => m.mount_point === selected.value));
const nodes = computed(() => {
  const at = layout(steps.value, mounts.value);
  const place = (id: string): { x: number; y: number } => at[id] ?? { x: 0, y: 0 };
  return [
    ...steps.value.map((step) => ({
      id: step.step_id,
      type: "step",
      position: place(step.step_id),
      data: {
        step,
        issues: byStep.value.get(step.step_id) ?? [],
        diffMark: diffMarks.value.get(step.step_id) ?? null,
      },
      draggable: false,
    })),
    ...mounts.value.map((mount) => ({
      id: mount.mount_point,
      type: "mount",
      position: place(mount.mount_point),
      data: {
        mount,
        issues: byStep.value.get(mount.mount_point) ?? [],
        diffMark: diffMarks.value.get(mount.mount_point) ?? null,
        // Shown, not enforced: the pin is the Rating Version's act (RL-1835 (ii) 3).
        pinned: props.subGraphPins.includes(mount.ref),
      },
      draggable: false,
    })),
  ];
});
const edges = computed(() =>
  edgesOf(steps.value, mounts.value).map(({ conditional, ...edge }) => ({
    ...edge,
    ...(conditional ? { style: { strokeDasharray: "6 4" } } : {}),
  })),
);

const { fitView } = useVueFlow();

function emitSteps(next: RatingStep[]): void {
  emit("update:draft", { ...props.draft, steps: next });
}

function select(id: string): void {
  selected.value = id;
  void fitView({ nodes: [id], duration: 0 });
}

function replace(step: RatingStep): void {
  const id = selected.value;
  emitSteps(steps.value.map((s) => (s.step_id === id ? step : s)));
  if (id !== null && step.step_id !== id) {
    added.value.delete(id);
    added.value.add(step.step_id);
    selected.value = step.step_id;
  }
}

function emitMounts(next: SubGraphRef[]): void {
  emit("update:draft", { ...props.draft, sub_graphs: next });
}

function remove(id: string): void {
  if (mounts.value.some((m) => m.mount_point === id)) {
    emitMounts(mounts.value.filter((m) => m.mount_point !== id));
  } else {
    emitSteps(steps.value.filter((s) => s.step_id !== id));
  }
  if (selected.value === id) selected.value = null;
}

function replaceMount(mount: SubGraphRef): void {
  const id = selected.value;
  emitMounts(mounts.value.map((m) => (m.mount_point === id ? mount : m)));
  selected.value = mount.mount_point;
}

function addMount(): void {
  const pin = props.subGraphPins[0];
  if (pin === undefined) return;
  const taken = new Set([...steps.value.map((s) => s.step_id), ...mounts.value.map((m) => m.mount_point)]);
  let n = 1;
  while (taken.has(`m_new_${n}`)) n += 1;
  const id = `m_new_${n}`;
  emitMounts([...mounts.value, { ref: pin, mount_point: id, inputs: {}, outputs: {} }]);
  selected.value = id;
}

// A new step starts with its text fields empty (the required-field gaps then block a save).
const EMPTY = "";

function blank(type: (typeof STEP_TYPES)[number], step_id: string): RatingStep {
  const common = { step_id, label: `New ${type} step` };
  switch (type) {
    case "input":
      return { ...common, type, input_name: "", on_missing: "error" };
    case "lookup":
      return { ...common, type, reference_table_ref: "", key_expr: [], as_at: "", on_miss: "error" };
    case "table":
      return {
        ...common,
        type,
        rate_table_ref: props.rateTablePins[0] ?? "",
        key_expr: [],
        on_miss: "error",
      };
    case "expression":
      return { ...common, type, expr: EMPTY, result_type: "decimal" };
    case "model_call":
      return { ...common, type, mode: props.versionMode, feature_map: {} };
    case "constraint":
      return { ...common, type, condition: EMPTY, on_violation: "error", reason_code: "" };
    case "output":
      return { ...common, type, output_name: "", rounding: { mode: "half_even", dp: 0 } };
  }
}

function add(): void {
  const taken = new Set(steps.value.map((s) => s.step_id));
  let n = 1;
  while (taken.has(`s_new_${n}`)) n += 1;
  const id = `s_new_${n}`;
  added.value.add(id);
  emitSteps([...steps.value, blank(nextType.value, id)]);
  selected.value = id;
}

function replaceContract(contract: RatingAlgorithmDraft["input_contract"]): void {
  emit("update:draft", { ...props.draft, input_contract: contract });
}
</script>

<template>
  <div class="grid gap-4 lg:grid-cols-[1fr_22rem]">
    <div>
      <div
        class="h-[28rem] rounded-md border border-slate-300 bg-slate-50"
        role="group"
        aria-label="Graph drawing of the steps; use the step list to move through them"
      >
        <VueFlow
          :nodes="nodes"
          :edges="edges"
          :nodes-connectable="false"
          :elements-selectable="false"
          :nodes-draggable="false"
        >
          <template #node-step="nodeProps">
            <StepNode :data="nodeProps.data" />
          </template>
          <template #node-mount="nodeProps">
            <MountNode :data="nodeProps.data" />
          </template>
        </VueFlow>
      </div>
      <p
        aria-live="polite"
        class="mt-2 text-sm text-slate-700"
      >
        {{ issueSummary }}
      </p>
      <GraphIssues
        :issues="graphLevel"
        :pending="pending"
      />
      <section
        class="mt-4"
        aria-labelledby="dd-outputs"
      >
        <h3
          id="dd-outputs"
          class="text-sm font-medium text-slate-700"
        >
          Declared outputs
        </h3>
        <ul class="mt-1 list-disc pl-5 text-sm text-slate-600">
          <li
            v-for="output in draft.outputs"
            :key="output.name"
          >
            {{ output.name }} ({{ output.type }})
          </li>
        </ul>
      </section>
    </div>

    <div class="space-y-4">
      <NodeNavigator
        :steps="steps"
        :mounts="mounts"
        :selected="selected"
        :issue-counts="issueCounts"
        @select="select"
        @remove="remove"
      />
      <DiffOverlay
        :slug="draft.slug"
        :version="draft.version"
        @diff="diff = $event"
      />
      <div class="flex items-end gap-2">
        <div class="flex-1">
          <label
            for="dd-add-type"
            class="mb-1 block text-sm font-medium text-slate-700"
          >Step type to add</label>
          <select
            id="dd-add-type"
            v-model="nextType"
            class="w-full rounded-md border border-slate-300 px-2 py-1 text-sm"
          >
            <option
              v-for="type in STEP_TYPES"
              :key="type"
              :value="type"
            >
              {{ type }}
            </option>
          </select>
        </div>
        <button
          type="button"
          class="rounded-md border border-slate-300 bg-white px-3 py-1 text-sm"
          @click="add"
        >
          Add step
        </button>
      </div>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="rounded-md border border-slate-300 bg-white px-3 py-1 text-sm disabled:opacity-50"
          :disabled="subGraphPins.length === 0"
          @click="addMount"
        >
          Add sub-graph mount
        </button>
        <p
          v-if="subGraphPins.length === 0"
          class="text-sm text-slate-700"
        >
          This Rating Version pins no sub-graph
        </p>
      </div>
      <MountInspector
        v-if="currentMount"
        :mount="currentMount"
        :sub-graph-pins="subGraphPins"
        @update:mount="replaceMount"
      />
      <StepInspector
        v-else-if="current"
        :step="current"
        :is-new="added.has(current.step_id)"
        :input-contract="draft.input_contract"
        :rate-table-pins="rateTablePins"
        :version-mode="versionMode"
        @update:step="replace"
        @update:input-contract="replaceContract"
      />
      <p
        v-else
        class="text-sm text-slate-500"
      >
        Select a step or mount to edit it.
      </p>
    </div>
  </div>
</template>
