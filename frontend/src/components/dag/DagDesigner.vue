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

import { edgesOf, layout } from "./graph";
import DiffOverlay from "./DiffOverlay.vue";
import GraphIssues from "./GraphIssues.vue";
import NodeNavigator from "./NodeNavigator.vue";
import StepInspector from "./StepInspector.vue";
import StepNode from "./StepNode.vue";
import { useGraphValidation } from "./useGraphValidation";

const props = defineProps<{
  draft: RatingAlgorithmDraft;
  versionMode: ModelReferenceMode;
  rateTablePins: string[];
}>();

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
  return marks;
});

const steps = computed(() => props.draft.steps);
const current = computed(() => steps.value.find((s) => s.step_id === selected.value));
const nodes = computed(() => {
  const at = layout(steps.value);
  return steps.value.map((step) => ({
    id: step.step_id,
    type: "step",
    position: at[step.step_id] ?? { x: 0, y: 0 },
    data: {
      step,
      issues: byStep.value.get(step.step_id) ?? [],
      diffMark: diffMarks.value.get(step.step_id) ?? null,
    },
    draggable: false,
  }));
});
const edges = computed(() => edgesOf(steps.value));

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

function remove(id: string): void {
  emitSteps(steps.value.filter((s) => s.step_id !== id));
  if (selected.value === id) selected.value = null;
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
      <StepInspector
        v-if="current"
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
        Select a step to edit it.
      </p>
    </div>
  </div>
</template>
