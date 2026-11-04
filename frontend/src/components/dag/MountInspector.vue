<script setup lang="ts">
/**
 * Edits one sub-graph mount (RL-1835 (i) 5; (iii) 1-2). The version options are the Rating
 * Version's sub-graph pins; the port rows are the pinned fragment's own ports, read through the
 * generated `SubGraph` type. Stateless: every edit emits a whole mount derived from the prop.
 */
import { ref, watch } from "vue";

import { getSubGraph, type SubGraph, type SubGraphRef } from "@/api/subGraphs";

import { parseRef } from "./graph";

const PURPOSES = ["mid_term_adjustment", "cancellation"] as const;

const props = defineProps<{ mount: SubGraphRef; subGraphPins: string[] }>();
const emit = defineEmits<{ "update:mount": [mount: SubGraphRef] }>();

const fragment = ref<SubGraph | null>(null);
const failed = ref(false);

let sequence = 0;
watch(
  () => props.mount.ref,
  async (ref_) => {
    sequence += 1;
    const mine = sequence;
    fragment.value = null;
    failed.value = false;
    try {
      const { slug, version } = parseRef(ref_);
      const loaded = await getSubGraph(slug, version);
      if (mine === sequence) fragment.value = loaded;
    } catch {
      if (mine === sequence) failed.value = true;
    }
  },
  { immediate: true },
);

function edit(changes: Partial<SubGraphRef>): void {
  emit("update:mount", { ...props.mount, ...changes });
}

function setRef(next: string): void {
  const same = parseRef(next).slug === parseRef(props.mount.ref).slug;
  edit(same ? { ref: next } : { ref: next, inputs: {}, outputs: {} });
}

function setInput(port: string, parent: string): void {
  edit({ inputs: { ...(props.mount.inputs ?? {}), [port]: parent } });
}

function setOutput(port: string, parent: string): void {
  const outputs = { ...(props.mount.outputs ?? {}) };
  if (parent === "") delete outputs[port];
  else outputs[port] = parent;
  edit({ outputs });
}

function togglePurpose(purpose: (typeof PURPOSES)[number], on: boolean): void {
  const kept = PURPOSES.filter((p) => (p === purpose ? on : (props.mount.purposes ?? []).includes(p)));
  // None checked means every purpose: the key is omitted, never `[]` (SubGraphRef refuses it).
  const next = { ...props.mount };
  if (kept.length === 0) delete next.purposes;
  else next.purposes = [...kept];
  emit("update:mount", next);
}

const field = "w-full rounded-md border border-slate-500 px-2 py-1 text-sm";
</script>

<template>
  <form
    class="space-y-3"
    :aria-label="`Inspector for ${mount.mount_point}`"
    @submit.prevent
  >
    <div>
      <label
        for="mi-version"
        class="mb-1 block text-sm font-medium text-slate-700"
      >Sub-graph version</label>
      <select
        id="mi-version"
        :value="mount.ref"
        :class="field"
        @change="setRef(($event.target as HTMLSelectElement).value)"
      >
        <option
          v-for="pin in subGraphPins"
          :key="pin"
          :value="pin"
        >
          {{ pin }}
        </option>
      </select>
      <p class="mt-1 text-xs text-slate-500">
        Only the sub-graph versions this Rating Version pins.
      </p>
    </div>

    <div>
      <label
        for="mi-point"
        class="mb-1 block text-sm font-medium text-slate-700"
      >Mount point</label>
      <input
        id="mi-point"
        type="text"
        :value="mount.mount_point"
        :class="field"
        @input="edit({ mount_point: ($event.target as HTMLInputElement).value })"
      >
    </div>

    <p
      v-if="failed"
      role="alert"
      class="text-sm text-red-800"
    >
      The sub-graph could not be loaded
    </p>
    <template v-if="fragment">
      <fieldset class="space-y-2">
        <legend class="text-sm font-medium text-slate-700">
          Input ports
        </legend>
        <input
          v-for="port in fragment.inputs"
          :key="port.name"
          type="text"
          :aria-label="`Input ${port.name} (${port.type})`"
          placeholder="parent name"
          :value="mount.inputs?.[port.name] ?? ''"
          :class="field"
          @input="setInput(port.name, ($event.target as HTMLInputElement).value)"
        >
      </fieldset>
      <fieldset class="space-y-2">
        <legend class="text-sm font-medium text-slate-700">
          Output ports
        </legend>
        <input
          v-for="port in fragment.outputs"
          :key="port.name"
          type="text"
          :aria-label="`Output ${port.name} (${port.type})`"
          placeholder="parent name (optional)"
          :value="mount.outputs?.[port.name] ?? ''"
          :class="field"
          @input="setOutput(port.name, ($event.target as HTMLInputElement).value)"
        >
      </fieldset>
    </template>

    <fieldset>
      <legend class="text-sm font-medium text-slate-700">
        Purposes
      </legend>
      <p class="text-xs text-slate-500">
        None checked: every purpose.
      </p>
      <label
        v-for="purpose in PURPOSES"
        :key="purpose"
        class="mr-3 inline-flex items-center gap-1 text-sm"
      >
        <input
          type="checkbox"
          :checked="(mount.purposes ?? []).includes(purpose)"
          @change="togglePurpose(purpose, ($event.target as HTMLInputElement).checked)"
        >{{ purpose }}
      </label>
    </fieldset>
  </form>
</template>
