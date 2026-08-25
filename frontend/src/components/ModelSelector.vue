<script setup lang="ts">
/**
 * Which model's interaction candidates the panel shows.
 *
 * The workbench is addressed by **Dataset Version**; interaction candidates live on a
 * per-**Model** transparency artifact, and a version may carry many models. `GET /models`
 * cannot filter by dataset version, so the filtering happens here — `OQ-MODEL-40`.
 *
 * **The default is the first row, and that means "most recent" only because the route says
 * so.** `Model` carries no timestamp; `list_models` orders by a UUIDv7 id. So nothing here
 * sorts, and `modelsForVersion` preserves the order it was given. Status appears in the
 * labels, where it informs a choice — never in the default, where it would silently surface
 * an older analysis while newer work exists.
 *
 * **A truncated walk says so.** An empty selector must not be readable as "this version has
 * no models" when the walk simply stopped early; that conflation is the defect
 * `OQ-MODEL-40` records, and the same one `OQ-MODEL-35` records one route over.
 */
import { computed, onMounted, ref, watch } from "vue";

import { listModels, modelsForVersion, type Model } from "@/api/models";
import { ProblemError } from "@/api/problem";
import FormField from "@/components/FormField.vue";

const props = defineProps<{
  datasetVersionId: string;
  /** Preselects when the actuary arrived from a model's own page. */
  preselect?: string | undefined;
}>();

const emit = defineEmits<{ "update:selected": [Model | null] }>();

const models = ref<Model[]>([]);
const truncated = ref(false);
const failed = ref(false);
const chosen = ref<string>("");

const selected = computed(
  () => models.value.find((model) => model.id === chosen.value) ?? null,
);

watch(selected, (model) => emit("update:selected", model));

onMounted(async () => {
  try {
    const page = await listModels();
    models.value = modelsForVersion(page, props.datasetVersionId);
    truncated.value = page.truncated;
    // The first is the most recent — see the note above on why that holds. A `preselect`
    // that is not on this version is ignored rather than honoured: it would show an
    // artifact belonging to different data.
    const wanted = models.value.find((model) => model.id === props.preselect);
    chosen.value = wanted?.id ?? models.value[0]?.id ?? "";
  } catch (caught) {
    if (!(caught instanceof ProblemError)) throw caught;
    failed.value = true;
  }
});
</script>

<template>
  <div>
    <FormField
      field-id="workbench-model"
      label="Model"
      help="Interaction candidates come from a model's transparency artifact, so they are a
            property of one fit rather than of the dataset version."
    >
      <select
        id="workbench-model"
        v-model="chosen"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
        <option value="">
          No model selected
        </option>
        <option
          v-for="model in models"
          :key="model.id"
          :value="model.id"
        >
          {{ model.model_family_slug }}@{{ model.version }} — {{ model.status }}
        </option>
      </select>
    </FormField>

    <p
      v-if="truncated"
      class="mt-1 text-xs text-amber-700"
    >
      More models exist than were loaded, so this list may be incomplete.
    </p>

    <p
      v-else-if="!models.length && !failed"
      class="mt-1 text-xs text-slate-500"
    >
      No models have been fitted on this dataset version.
    </p>

    <p
      v-if="failed"
      class="mt-1 text-xs text-amber-700"
    >
      Models could not be loaded.
    </p>
  </div>
</template>
