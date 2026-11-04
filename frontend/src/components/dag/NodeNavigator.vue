<script setup lang="ts">
/**
 * The keyboard path to every node (RS-1269 F2 condition 2; `00` NFR-463). A listbox of the
 * steps in graph order with a roving active option: arrows, Home/End, a typed `step_id`
 * prefix, Enter to select, Delete to remove after a confirmation.
 */
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";

import type { RatingStep } from "@/api/ratingAlgorithms";
import type { SubGraphRef } from "@/api/subGraphs";

import { graphOrder } from "./graph";

const props = withDefaults(
  defineProps<{
    steps: RatingStep[];
    mounts?: SubGraphRef[];
    selected: string | null;
    issueCounts?: ReadonlyMap<string, number>;
  }>(),
  { mounts: () => [], issueCounts: () => new Map<string, number>() },
);

/** A step or a sub-graph mount (RL-1835 (i) 6: the keyboard path covers mounts). */
interface Entry {
  id: string;
  label: string;
  mount: boolean;
}

function optionName(entry: Entry): string {
  const n = props.issueCounts.get(entry.id) ?? 0;
  const base = `${entry.id} ${entry.label}`;
  return n === 0 ? base : `${base}, ${n} ${n === 1 ? "issue" : "issues"}`;
}
const emit = defineEmits<{ select: [stepId: string]; remove: [stepId: string] }>();

const TYPEAHEAD_MS = 500;

const order = computed(() => graphOrder(props.steps, props.mounts));
const entries = computed(() => {
  const byId = new Map<string, Entry>([
    ...props.steps.map((s) => [s.step_id, { id: s.step_id, label: s.label, mount: false }] as const),
    ...props.mounts.map((m) => [m.mount_point, { id: m.mount_point, label: `sub-graph ${m.ref}`, mount: true }] as const),
  ]);
  return order.value.map((id) => byId.get(id) as Entry);
});
const confirmingMount = computed(() => props.mounts.some((m) => m.mount_point === confirming.value));

const active = ref<string | null>(props.selected ?? order.value[0] ?? null);
watch(
  () => props.selected,
  (id) => {
    if (id !== null) active.value = id;
  },
);
watch(order, (ids, before) => {
  if (active.value !== null && ids.includes(active.value)) return;
  // The removed step's neighbour, not the first step (4.1.3 / 2.4.3).
  const was = before.indexOf(active.value ?? "");
  active.value = ids[Math.min(Math.max(was, 0), ids.length - 1)] ?? null;
});

// Keep the active option in view inside the scrolling list (2.4.7, 2.4.11).
watch(active, async (id) => {
  if (id === null) return;
  await nextTick();
  document.getElementById(`nav-${id}`)?.scrollIntoView?.({ block: "nearest" });
});

const list = ref<HTMLElement | null>(null);
const confirming = ref<string | null>(null);
const removed = ref("");
const cancel = ref<HTMLButtonElement | null>(null);

let buffer = "";
let timer: ReturnType<typeof setTimeout> | undefined;
onBeforeUnmount(() => clearTimeout(timer));

function move(to: number): void {
  const ids = order.value;
  if (ids.length === 0) return;
  active.value = ids[Math.min(Math.max(to, 0), ids.length - 1)] ?? null;
}

function typeahead(key: string): void {
  clearTimeout(timer);
  buffer += key.toLowerCase();
  timer = setTimeout(() => {
    buffer = "";
  }, TYPEAHEAD_MS);
  const hit = order.value.find((id) => id.toLowerCase().startsWith(buffer));
  if (hit !== undefined) active.value = hit;
}

async function ask(): Promise<void> {
  if (active.value === null) return;
  confirming.value = active.value;
  await nextTick();
  cancel.value?.focus();
}

async function close(): Promise<void> {
  confirming.value = null;
  await nextTick();
  list.value?.focus();
}

function confirmRemove(): void {
  if (confirming.value !== null) {
    removed.value = `Removed ${confirmingMount.value ? "mount" : "step"} ${confirming.value}`;
    emit("remove", confirming.value);
  }
  void close();
}

function onKeydown(event: KeyboardEvent): void {
  const at = active.value === null ? 0 : order.value.indexOf(active.value);
  switch (event.key) {
    case "ArrowDown":
      move(at + 1);
      break;
    case "ArrowUp":
      move(at - 1);
      break;
    case "Home":
      move(0);
      break;
    case "End":
      move(order.value.length - 1);
      break;
    case "Enter":
      if (active.value !== null) emit("select", active.value);
      break;
    case "Delete":
      void ask();
      break;
    default:
      if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) {
        typeahead(event.key);
        break;
      }
      return;
  }
  event.preventDefault();
}
</script>

<template>
  <div>
    <p
      role="status"
      class="sr-only"
    >
      {{ removed }}
    </p>
    <ul
      ref="list"
      role="listbox"
      aria-label="Steps in graph order"
      tabindex="0"
      :aria-activedescendant="active === null ? undefined : `nav-${active}`"
      class="max-h-64 overflow-auto rounded-md border border-slate-300 bg-white p-1 text-sm focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-700"
      @keydown="onKeydown"
    >
      <li
        v-for="entry in entries"
        :id="`nav-${entry.id}`"
        :key="entry.id"
        role="option"
        :aria-label="optionName(entry)"
        :aria-selected="entry.id === selected"
        class="cursor-pointer rounded border-l-4 px-2 py-1"
        :class="[
          entry.id === active ? 'bg-sky-100 text-sky-900 outline outline-2 outline-sky-700' : '',
          entry.id === selected ? 'border-sky-700 font-semibold' : 'border-transparent',
        ]"
        @click="active = entry.id; emit('select', entry.id)"
      >
        <span class="font-mono text-xs">{{ entry.id }}</span>
        <span class="ml-2 text-slate-600">{{ entry.label }}</span>
      </li>
    </ul>
    <div
      v-if="confirming !== null"
      role="alertdialog"
      aria-labelledby="nav-confirm-title"
      aria-describedby="nav-confirm-title"
      class="mt-2 rounded-md border border-red-200 bg-red-50 p-3"
      @keydown.esc="close"
    >
      <p
        id="nav-confirm-title"
        class="text-sm text-red-800"
      >
        Remove {{ confirmingMount ? "mount" : "step" }} {{ confirming }}? Steps that consume what it produces are left unresolved.
      </p>
      <div class="mt-2 flex gap-2">
        <button
          ref="cancel"
          type="button"
          class="rounded-md border border-slate-300 bg-white px-3 py-1 text-sm"
          @click="close"
        >
          Cancel
        </button>
        <button
          type="button"
          class="rounded-md bg-red-700 px-3 py-1 text-sm text-white"
          @click="confirmRemove"
        >
          {{ confirmingMount ? "Remove mount" : "Remove step" }}
        </button>
      </div>
    </div>
  </div>
</template>
