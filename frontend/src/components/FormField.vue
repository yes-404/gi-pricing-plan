<script setup lang="ts">
/**
 * A label bound to one control, with optional help text.
 *
 * The only form primitive this slice extracts. `W6b-4a`'s Decision 3: extract what the
 * slice itself uses twice, and nothing speculative — every control in the builder needs a
 * label wired to it, and no other shape repeats. There is deliberately **no** `Select`:
 * the three objective controls take three different option types (`GlmSpec`'s `family` ×
 * `link`, `GbmSpec`'s `GbmFunctionRef`, `EbmSpec`'s `"rmse" | "mae"`), so a shared select
 * would be a generic wrapper around three unrelated unions rather than one abstraction.
 *
 * The binding is by `id`, not by nesting the control inside the `<label>`. Both associate
 * a label with a control, but only the explicit `for`/`id` pair survives a control that
 * renders extra interactive elements beside it — and the id is required rather than
 * generated, so a caller cannot accidentally produce two fields sharing one.
 */
defineProps<{
  /** The control's `id`. Required: it is what `for` points at. */
  fieldId: string;
  label: string;
  /** Shown under the control. For guidance, never for errors — those are problems. */
  help?: string;
}>();
</script>

<template>
  <div class="mb-4">
    <label
      :for="fieldId"
      class="mb-1 block text-sm font-medium text-slate-700"
    >{{ label }}</label>

    <slot />

    <p
      v-if="help"
      class="mt-1 text-xs text-slate-500"
    >
      {{ help }}
    </p>
  </div>
</template>
