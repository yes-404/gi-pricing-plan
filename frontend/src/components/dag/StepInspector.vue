<script setup lang="ts">
/**
 * One form section per step type (03 §3.2). Every edit emits a new step object; nothing is
 * mutated. Required-field gaps show as `problems` (presence only: graph rules are the
 * server's, RL-1474). A decimal is edited and sent as the string typed (`00` FR-10, FR-21).
 */
import { computed } from "vue";

import type {
  InputContractField,
  ModelReferenceMode,
  RatingInputType,
  RatingStep,
  RoundMode,
} from "@/api/ratingAlgorithms";
import FormField from "@/components/FormField.vue";

import { names } from "./graph";
import { stepProblems } from "./problems";

const props = defineProps<{
  step: RatingStep;
  isNew: boolean;
  inputContract: InputContractField[];
  rateTablePins: string[];
  versionMode: ModelReferenceMode;
}>();

const emit = defineEmits<{
  "update:step": [step: RatingStep];
  "update:inputContract": [contract: InputContractField[]];
}>();

// Pinned to the generated unions: a member added server-side fails type-check here.
const INPUT_TYPES = ["int", "decimal", "string", "date", "bool", "enum"] as const satisfies
  readonly RatingInputType[];
const ROUND_MODES = ["half_even", "half_up", "ceiling", "floor"] as const satisfies
  readonly RoundMode[];
const ON_MISSING = ["error", "default", "null"] as const;
const ON_MISS = ["error", "default"] as const;
const ON_VIOLATION = ["clamp", "decline", "error"] as const;

const control =
  "w-full rounded-md border border-slate-300 px-2 py-1 text-sm focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-sky-700";

const problems = computed(() => stepProblems(props.step));
/** `aria-invalid` for the field a problem names (3.3.1): problems start with the field name. */
const invalid = (field: string): true | undefined =>
  problems.value.some((p) => p.startsWith(field)) ? true : undefined;

function patch(fields: Record<string, unknown>): void {
  const mode =
    props.isNew && props.step.type === "model_call" ? { mode: props.versionMode } : {};
  emit("update:step", { ...props.step, ...fields, ...mode } as RatingStep);
}

const value = (event: Event): string =>
  (event.target as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement).value;
const list = (text: string): string[] =>
  text
    .split(",")
    .map((part) => part.trim())
    .filter((part) => part !== "");

const entry = computed(() =>
  props.step.type === "input"
    ? props.inputContract.find((field) => field.name === (props.step as { input_name: string }).input_name)
    : undefined,
);

function patchEntry(fields: Partial<InputContractField>): void {
  const current = entry.value;
  if (current === undefined) return;
  emit(
    "update:inputContract",
    props.inputContract.map((field) => (field === current ? { ...field, ...fields } : field)),
  );
}

const dateInputs = computed(() =>
  props.inputContract.filter((field) => field.type === "date").map((field) => field.name),
);

const featureMapText = computed(() =>
  props.step.type === "model_call"
    ? Object.entries(props.step.feature_map ?? {})
        .map(([feature, source]) => `${feature}=${source}`)
        .join("\n")
    : "",
);

function featureMap(text: string): Record<string, string> {
  const map: Record<string, string> = {};
  for (const line of text.split("\n")) {
    const at = line.indexOf("=");
    if (at > 0) map[line.slice(0, at).trim()] = line.slice(at + 1).trim();
  }
  return map;
}
</script>

<template>
  <form
    class="space-y-1"
    :aria-label="`Inspector for ${step.step_id}`"
    @submit.prevent
  >
    <FormField
      field-id="si-step-id"
      label="Step id"
      v-bind="isNew ? {} : { help: 'Fixed once the step exists (FR-215).' }"
    >
      <input
        id="si-step-id"
        :class="control"
        :value="step.step_id"
        :readonly="!isNew"
        @input="isNew && patch({ step_id: value($event) })"
      >
    </FormField>
    <FormField
      field-id="si-label"
      label="Label"
    >
      <input
        id="si-label"
        :class="control"
        :value="step.label"
        @input="patch({ label: value($event) })"
      >
    </FormField>
    <FormField
      field-id="si-consumes"
      label="Consumes"
      help="Names this step reads, comma separated. Edges are drawn from these."
    >
      <input
        id="si-consumes"
        :class="control"
        :value="names(step.consumes).join(', ')"
        @input="patch({ consumes: list(value($event)) })"
      >
    </FormField>
    <FormField
      field-id="si-produces"
      label="Produces"
      help="Names this step makes, comma separated."
    >
      <input
        id="si-produces"
        :class="control"
        :value="names(step.produces).join(', ')"
        @input="patch({ produces: list(value($event)) })"
      >
    </FormField>

    <template v-if="step.type === 'input'">
      <FormField
        field-id="si-input-name"
        label="Input name"
      >
        <input
          id="si-input-name"
          :class="control"
          :value="step.input_name"
          @input="patch({ input_name: value($event) })"
        >
      </FormField>
      <FormField
        field-id="si-on-missing"
        label="When missing"
      >
        <select
          id="si-on-missing"
          :class="control"
          :value="step.on_missing"
          @change="patch({ on_missing: value($event) })"
        >
          <option
            v-for="option in ON_MISSING"
            :key="option"
            :value="option"
          >
            {{ option }}
          </option>
        </select>
      </FormField>
      <fieldset
        v-if="entry"
        class="rounded-md border border-slate-200 p-3"
      >
        <legend class="px-1 text-sm font-medium text-slate-700">
          Input contract: {{ entry.name }}
        </legend>
        <FormField
          field-id="si-ic-type"
          label="Input type"
        >
          <select
            id="si-ic-type"
            :class="control"
            :value="entry.type"
            @change="patchEntry({ type: value($event) as RatingInputType })"
          >
            <option
              v-for="option in INPUT_TYPES"
              :key="option"
              :value="option"
            >
              {{ option }}
            </option>
          </select>
        </FormField>
        <div class="mb-4 flex items-center gap-2">
          <input
            id="si-ic-nullable"
            type="checkbox"
            :checked="entry.nullable ?? false"
            @change="patchEntry({ nullable: ($event.target as HTMLInputElement).checked })"
          >
          <label
            for="si-ic-nullable"
            class="text-sm text-slate-700"
          >Nullable</label>
        </div>
        <FormField
          field-id="si-ic-min"
          label="Minimum"
        >
          <input
            id="si-ic-min"
            :class="control"
            inputmode="decimal"
            :value="entry.min ?? ''"
            @input="patchEntry({ min: value($event) === '' ? null : value($event) })"
          >
        </FormField>
        <FormField
          field-id="si-ic-max"
          label="Maximum"
        >
          <input
            id="si-ic-max"
            :class="control"
            inputmode="decimal"
            :value="entry.max ?? ''"
            @input="patchEntry({ max: value($event) === '' ? null : value($event) })"
          >
        </FormField>
        <FormField
          field-id="si-ic-domain"
          label="Domain"
          help="Allowed values, comma separated."
        >
          <input
            id="si-ic-domain"
            :class="control"
            :value="(entry.domain ?? []).join(', ')"
            @input="patchEntry({ domain: list(value($event)) })"
          >
        </FormField>
        <FormField
          field-id="si-ic-description"
          label="Description"
        >
          <input
            id="si-ic-description"
            :class="control"
            :value="entry.description ?? ''"
            @input="patchEntry({ description: value($event) })"
          >
        </FormField>
      </fieldset>
    </template>

    <template v-else-if="step.type === 'lookup'">
      <FormField
        field-id="si-lookup-table"
        label="Reference table"
      >
        <input
          id="si-lookup-table"
          :class="control"
          :value="step.reference_table_ref"
          @input="patch({ reference_table_ref: value($event) })"
        >
      </FormField>
      <FormField
        field-id="si-key-expr"
        label="Key expressions"
        help="One per key column, comma separated."
      >
        <input
          id="si-key-expr"
          :class="control"
          :value="(step.key_expr ?? []).join(', ')"
          @input="patch({ key_expr: list(value($event)) })"
        >
      </FormField>
      <FormField
        field-id="si-as-at"
        label="As at (date input)"
        help="Required (FR-221): a declared date input, never 'now'."
      >
        <select
          id="si-as-at"
          :class="control"
          :aria-invalid="invalid('as_at')"
          aria-describedby="si-problems"
          :value="step.as_at"
          @change="patch({ as_at: value($event) })"
        >
          <option
            v-if="step.as_at !== '' && !dateInputs.includes(step.as_at)"
            :value="step.as_at"
          >
            {{ step.as_at }}
          </option>
          <option
            value=""
            disabled
          >
            Choose a date input
          </option>
          <option
            v-for="option in dateInputs"
            :key="option"
            :value="option"
          >
            {{ option }}
          </option>
        </select>
      </FormField>
      <FormField
        field-id="si-on-miss"
        label="On miss"
      >
        <select
          id="si-on-miss"
          :class="control"
          :value="step.on_miss"
          @change="patch({ on_miss: value($event) })"
        >
          <option
            v-for="option in ON_MISS"
            :key="option"
            :value="option"
          >
            {{ option }}
          </option>
        </select>
      </FormField>
    </template>

    <template v-else-if="step.type === 'table'">
      <FormField
        field-id="si-rate-table"
        label="Rate table"
        help="Only the tables this Rating Version pins."
      >
        <select
          id="si-rate-table"
          :class="control"
          :aria-invalid="invalid('rate_table_ref')"
          aria-describedby="si-problems"
          :value="step.rate_table_ref"
          @change="patch({ rate_table_ref: value($event) })"
        >
          <option
            v-for="option in rateTablePins"
            :key="option"
            :value="option"
          >
            {{ option }}
          </option>
        </select>
      </FormField>
      <FormField
        field-id="si-table-keys"
        label="Key expressions"
        help="One per key column, comma separated. A banding reference is text."
      >
        <input
          id="si-table-keys"
          :class="control"
          :value="(step.key_expr ?? []).join(', ')"
          @input="patch({ key_expr: list(value($event)) })"
        >
      </FormField>
      <FormField
        field-id="si-table-miss"
        label="On miss"
      >
        <select
          id="si-table-miss"
          :class="control"
          :value="step.on_miss ?? 'error'"
          @change="patch({ on_miss: value($event) })"
        >
          <option
            v-for="option in ON_MISS"
            :key="option"
            :value="option"
          >
            {{ option }}
          </option>
        </select>
      </FormField>
    </template>

    <template v-else-if="step.type === 'expression'">
      <FormField
        field-id="si-expr"
        label="Expression"
        help="Text. The vocabulary is checked on the server at save."
      >
        <textarea
          id="si-expr"
          :class="control"
          rows="4"
          :value="step.expr"
          @input="patch({ expr: value($event) })"
        />
      </FormField>
      <FormField
        field-id="si-result-type"
        label="Result type"
      >
        <input
          id="si-result-type"
          :class="control"
          :value="step.result_type"
          @input="patch({ result_type: value($event) })"
        >
      </FormField>
    </template>

    <template v-else-if="step.type === 'model_call'">
      <FormField
        field-id="si-model-ref"
        label="Model"
      >
        <input
          id="si-model-ref"
          :class="control"
          :value="step.model_ref ?? ''"
          @input="patch({ model_ref: value($event) === '' ? null : value($event) })"
        >
      </FormField>
      <FormField
        field-id="si-peril-ref"
        label="Peril structure"
      >
        <input
          id="si-peril-ref"
          :class="control"
          :value="step.peril_structure_ref ?? ''"
          @input="patch({ peril_structure_ref: value($event) === '' ? null : value($event) })"
        >
      </FormField>
      <FormField
        field-id="si-features"
        label="Feature map"
        help="One per line: feature=source name."
      >
        <textarea
          id="si-features"
          :class="control"
          rows="4"
          :value="featureMapText"
          @input="patch({ feature_map: featureMap(value($event)) })"
        />
      </FormField>
      <p class="mb-4 text-sm text-slate-700">
        Model reference mode: {{ versionMode }} (set on the Rating Version, FR-223)
      </p>
      <p
        v-if="step.mode !== versionMode"
        role="status"
        class="mb-4 rounded-md border border-amber-300 bg-amber-50 p-2 text-sm text-amber-900"
      >
        This step declares mode {{ step.mode }}, but the Rating Version declares {{ versionMode }}.
        Compilation refuses the difference (FR-223).
      </p>
    </template>

    <template v-else-if="step.type === 'constraint'">
      <FormField
        field-id="si-condition"
        label="Condition"
      >
        <input
          id="si-condition"
          :class="control"
          :value="step.condition"
          @input="patch({ condition: value($event) })"
        >
      </FormField>
      <FormField
        field-id="si-on-violation"
        label="On violation"
      >
        <select
          id="si-on-violation"
          :class="control"
          :value="step.on_violation"
          @change="patch({ on_violation: value($event) })"
        >
          <option
            v-for="option in ON_VIOLATION"
            :key="option"
            :value="option"
          >
            {{ option }}
          </option>
        </select>
      </FormField>
      <FormField
        field-id="si-clamp-min"
        label="Clamp minimum"
      >
        <input
          id="si-clamp-min"
          :class="control"
          inputmode="decimal"
          :value="step.clamp_bounds?.min ?? ''"
          @input="patch({ clamp_bounds: { ...step.clamp_bounds, min: value($event) } })"
        >
      </FormField>
      <FormField
        field-id="si-clamp-max"
        label="Clamp maximum"
      >
        <input
          id="si-clamp-max"
          :class="control"
          inputmode="decimal"
          :value="step.clamp_bounds?.max ?? ''"
          @input="patch({ clamp_bounds: { ...step.clamp_bounds, max: value($event) } })"
        >
      </FormField>
      <FormField
        field-id="si-reason"
        label="Reason code"
        help="Required (FR-225)."
      >
        <input
          id="si-reason"
          :class="control"
          :aria-invalid="invalid('reason_code')"
          aria-describedby="si-problems"
          :value="step.reason_code"
          @input="patch({ reason_code: value($event) })"
        >
      </FormField>
    </template>

    <template v-else-if="step.type === 'output'">
      <FormField
        field-id="si-output-name"
        label="Output name"
      >
        <input
          id="si-output-name"
          :class="control"
          :value="step.output_name"
          @input="patch({ output_name: value($event) })"
        >
      </FormField>
      <FormField
        field-id="si-round-mode"
        label="Rounding mode"
        help="Required (FR-226)."
      >
        <select
          id="si-round-mode"
          :class="control"
          :aria-invalid="invalid('rounding mode')"
          aria-describedby="si-problems"
          :value="step.rounding.mode"
          @change="patch({ rounding: { ...step.rounding, mode: value($event) } })"
        >
          <option
            v-for="option in ROUND_MODES"
            :key="option"
            :value="option"
          >
            {{ option }}
          </option>
        </select>
      </FormField>
      <FormField
        field-id="si-round-dp"
        label="Decimal places (dp)"
        help="Required (FR-226)."
      >
        <input
          id="si-round-dp"
          :aria-invalid="invalid('rounding dp')"
          aria-describedby="si-problems"
          type="number"
          min="0"
          step="1"
          :class="control"
          :value="step.rounding.dp"
          @input="patch({ rounding: { ...step.rounding, dp: value($event) === '' ? Number.NaN : Number(value($event)) } })"
        >
      </FormField>
    </template>

    <ul
      v-if="problems.length > 0"
      id="si-problems"
      aria-label="Problems"
      class="mt-4 list-disc pl-5 text-sm text-red-700"
    >
      <li
        v-for="problem in problems"
        :key="problem"
      >
        {{ problem }}
      </li>
    </ul>
  </form>
</template>
