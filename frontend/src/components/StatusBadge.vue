<script setup lang="ts">
/**
 * A Dataset Version's status, as a badge.
 *
 * The tone map is keyed **`Record<DatasetStatus, string>`**, not `Record<string, string>`,
 * and that is the whole reason this component exists as a component. `DatasetStatus` is a
 * generated union with five members (`model-schema/datasets.py:56-61` →
 * `schema.d.ts`), and a map typed on it cannot omit one: the compiler enumerates the
 * members so a human does not have to remember to. `StatusBadge.test-d.ts` proves that
 * property by omitting a member and expecting the error — it has to live in a `.test-d.ts`,
 * because vitest's typecheck includes only that glob and a type assertion in a `.test.ts`
 * file is invisible to `pnpm test`.
 *
 * That is not a hypothetical. `DatasetDetailView` held this map inline, typed
 * `Record<string, string>`, with **four** of the five members — `failed` was missing and
 * fell through a `?? 'bg-slate-100'` fallback to *draft's own background*. A version whose
 * validation failed rendered in the same calm neutral as one nobody had touched yet, in the
 * view someone reads to decide whether data is fit to model on. The badge always carried the
 * status as text, so this was never a WCAG 1.4.1 failure — the word "failed" was on screen.
 * It was the visual channel saying "nothing has happened here" about the one state that
 * means something went wrong, which is the same shape as the `psiBand`-returns-"stable"
 * defect recorded in `01` §5.3's 2026-08-19 note.
 *
 * The text is always rendered, so colour is never the only channel (WCAG 2.2 AA, NFR-OVR-10).
 */
import type { DatasetStatus } from "@/api/datasets";

defineProps<{ status: DatasetStatus }>();

const TONE: Record<DatasetStatus, string> = {
  draft: "bg-slate-100 text-slate-700",
  validating: "bg-amber-100 text-amber-900",
  validated: "bg-emerald-100 text-emerald-900",
  failed: "bg-red-100 text-red-900",
  archived: "bg-slate-200 text-slate-600",
};
</script>

<template>
  <span
    :class="['rounded px-2 py-0.5 text-xs font-medium', TONE[status]]"
  >{{ status }}</span>
</template>
