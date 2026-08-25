<script setup lang="ts">
/**
 * `02` §5.3's Model spec builder — `/models/new`.
 *
 * Builds a Model Spec and asks `POST /model-specs/validate` whether it may be fitted,
 * before any compute is spent. `W6b-4a` covers the **builtin** objective arm; `W6b-4b`
 * adds custom objectives.
 *
 * **FR-MODEL-19's limb A is deliberately not implemented here.** The requirement sets
 * actuarial defaults per response type — severity → Gamma, `weight = claim_count`, and so
 * on — and **nothing in `model-schema` exposes that mapping**: `response` is a flat
 * optional field, the only response-keyed table is the objective *applicability* one
 * (the inverse relation), and both `GlmSpec` validators key off `family`, never
 * `response`. Authoring the mapping in TypeScript would make the frontend the source of
 * an actuarial fact (`CLAUDE.md` §2), so this form requires `response`, passes it through,
 * and leaves family/link/offset/weight as explicit choices. Scoped out with no owner.
 *
 * For the same reason there is **no family×link compatibility rule** here: none exists in
 * the contract, so one written here would be invented rather than enforced.
 */
import { computed, onMounted, ref, watch } from "vue";

import { listDatasets, listVersions, type Dataset } from "@/api/datasets";
import { listFactors, type Factor } from "@/api/models";
import {
  BUILTIN_GBM_OBJECTIVES,
  FAMILIES,
  LINKS,
  RESPONSES,
  validateSpec,
  type GlmFamily,
  type GlmLink,
  type ModelSpec,
  type SpecValidation,
} from "@/api/modelSpecs";
import { ProblemError } from "@/api/problem";
import { listSplits, type DatasetSplit } from "@/api/versions";
import FormField from "@/components/FormField.vue";
import SpecProblemList from "@/components/SpecProblemList.vue";

type ModelArm = "glm" | "gbm" | "ebm";

const datasets = ref<Dataset[]>([]);
const versions = ref<{ id: string; version: number }[]>([]);
const splits = ref<DatasetSplit[]>([]);
const factors = ref<Factor[]>([]);

const slug = ref("");
const datasetId = ref("");
const versionId = ref("");
const splitId = ref("");
const trainPart = ref("train");
const holdoutPart = ref("test");

const modelFamilySlug = ref("");
const responseColumn = ref("");
/** Required by this form even though `ModelSpecCommon.response` is optional — see above. */
const response = ref<NonNullable<ModelSpec["response"]> | "">("");
const offsetKind = ref<"none" | "log_column" | "column">("none");
const offsetColumn = ref("");
const weightKind = ref<"none" | "column">("none");
const weightColumn = ref("");
const chosenFactors = ref<string[]>([]);

const arm = ref<ModelArm>("glm");

/**
 * Three objective controls, one per arm, with no shared "objective" type.
 *
 * `model-schema` keeps the three apart and they are not three vocabularies behind one
 * idea: a GLM's `family` × `link` pair **is** its distributional assumption, a GBM's
 * objective is a named loss in a `GbmFunctionRef`, an EBM's is a two-member literal.
 * Normalising them here would create a fourth shape the contract does not have.
 */
// Derived, not spelled. These annotations were a **third** copy of the two unions —
// after the option arrays and the contract itself — and the copy that types the state is
// the one a wrong value flows out of.
const family = ref<GlmFamily>("poisson");
const link = ref<GlmLink>("log");
const tweediePower = ref(1.5);
const gbmBackend = ref<"xgboost" | "lightgbm">("xgboost");
/** FR-MODEL-26's builtin set. `reg:tweedie` alone carries a dependent parameter. */
const gbmObjective = ref("count:poisson");
const ebmObjective = ref<"rmse" | "mae">("rmse");

// The option lists live in `@/api/modelSpecs` and are imported above: a list the type test
// cannot see is a list the pin does not cover, and `objectiveVocabulary.test-d.ts` is what
// catches a member the contract *adds*.

const common = computed(() => ({
  model_family_slug: modelFamilySlug.value,
  dataset_version_id: versionId.value,
  response_column: responseColumn.value,
  ...(response.value ? { response: response.value } : {}),
  offset: offsetKind.value === "none"
    ? { kind: "none" as const }
    : { kind: offsetKind.value, column: offsetColumn.value },
  weight: weightKind.value === "none"
    ? { kind: "none" as const }
    : { kind: weightKind.value, column: weightColumn.value },
  factors: chosenFactors.value,
  ...(splitId.value
    ? {
      split_ref: {
        split_artifact_id: splitId.value,
        train_part: trainPart.value,
        holdout_part: holdoutPart.value,
      },
    }
    : {}),
}));

/**
 * `null` until the three required fields are present — no point asking before then.
 *
 * The casts are `unknown`-mediated and deliberate. `ModelSpec` is generated from the
 * **response** shape, where every server-side default is present and therefore typed as
 * required (`alpha`, `seed`, `method`, `loss_treatment`, …). A request body may omit them
 * and the server fills them in, so the request-shaped type and the response-shaped type
 * genuinely differ and only the latter is generated. The alternative — spelling out every
 * default here — would hand-write the contract's defaults into the frontend, which is
 * `CLAUDE.md` §2's prohibition and the thing this slice has been careful about elsewhere.
 * The cast is confined to these three returns and the fields above it are all typed.
 */
const spec = computed<ModelSpec | null>(() => {
  if (!modelFamilySlug.value || !versionId.value || !responseColumn.value) return null;

  if (arm.value === "glm") {
    return {
      ...common.value,
      model_type: "glm",
      family: family.value,
      link: link.value,
      ...(family.value === "tweedie"
        ? { family_params: { power: tweediePower.value } }
        : {}),
    } as unknown as ModelSpec;
  }
  if (arm.value === "gbm") {
    return {
      ...common.value,
      model_type: gbmBackend.value,
      objective: { kind: "builtin", name: gbmObjective.value },
    } as unknown as ModelSpec;
  }
  return {
    ...common.value,
    model_type: "ebm",
    objective: ebmObjective.value,
  } as unknown as ModelSpec;
});

const validation = ref<SpecValidation | null>(null);
const problem = ref<ProblemError | null>(null);
const checking = ref(false);

/**
 * Debounced validation, with the in-flight response **superseded** rather than raced.
 *
 * `02` §5.3 asks for validation "as the form is edited". Without the sequence guard a
 * slower earlier request can land after a faster later one and repaint the form with
 * problems belonging to a spec the analyst has already changed — a validator that shows
 * stale problems is worse than one that shows none, because the analyst edits against it.
 */
let sequence = 0;
let timer: ReturnType<typeof setTimeout> | undefined;

async function run(current: ModelSpec): Promise<void> {
  const mine = ++sequence;
  checking.value = true;
  try {
    const result = await validateSpec(current);
    if (mine !== sequence) return;
    validation.value = result;
    problem.value = null;
  } catch (caught) {
    if (mine !== sequence) return;
    if (!(caught instanceof ProblemError)) throw caught;
    problem.value = caught;
    validation.value = null;
  } finally {
    if (mine === sequence) checking.value = false;
  }
}

watch(spec, (current) => {
  if (timer) clearTimeout(timer);
  if (current === null) {
    validation.value = null;
    problem.value = null;
    return;
  }
  timer = setTimeout(() => void run(current), 300);
}, { deep: true });

/**
 * The actionable half of a problem, and the reason this view does not render
 * `title`/`detail` the way every other error surface here does.
 *
 * Measured against the running API: a spec the *type* refuses — Poisson with no offset —
 * comes back **422**, `title: "Request validation failed"`, `detail: "1 field(s) failed
 * validation."`, and the sentence that actually helps ("a Poisson model must declare an
 * offset (FR-MODEL-19 …)") **only** inside `errors[]`. The 404 for an absent dataset
 * version carries an empty `errors[]` and its meaning in `title`/`detail`.
 *
 * So the discriminator is the presence of field errors, not the status code and not the
 * `code` — `VALIDATION_FAILED` is raised by many routes for different things, while the
 * shape of the payload is exactly what separates the two cases. Rendering `title` and
 * `detail` alone would show "Request validation failed / 1 field(s) failed validation"
 * and discard the only sentence naming the problem.
 */
const fieldErrors = computed(() => problem.value?.fieldErrors ?? []);

async function loadVersions(): Promise<void> {
  versions.value = [];
  versionId.value = "";
  const chosen = datasets.value.find((d) => d.slug === slug.value);
  datasetId.value = chosen?.id ?? "";
  if (!slug.value) return;
  const page = await listVersions(slug.value);
  versions.value = page.items.map((v: { id: string; version: number }) => ({
    id: v.id,
    version: v.version,
  }));
  factors.value = datasetId.value ? await listFactors(datasetId.value) : [];
}

async function loadSplits(): Promise<void> {
  splits.value = versionId.value ? await listSplits(versionId.value) : [];
  splitId.value = "";
}

onMounted(async () => {
  datasets.value = (await listDatasets({ limit: 200 })).items;
});
</script>

<template>
  <section class="max-w-3xl">
    <h1 class="mb-6 text-xl font-semibold tracking-tight">
      New model spec
    </h1>

    <FormField
      field-id="dataset"
      label="Dataset"
    >
      <select
        id="dataset"
        v-model="slug"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
        @change="loadVersions"
      >
        <option value="">
          Choose a dataset
        </option>
        <option
          v-for="d in datasets"
          :key="d.id"
          :value="d.slug"
        >
          {{ d.name || d.slug }}
        </option>
      </select>
    </FormField>

    <FormField
      field-id="version"
      label="Dataset version"
      help="Modelling references a Dataset Version, never a Dataset."
    >
      <select
        id="version"
        v-model="versionId"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
        @change="loadSplits"
      >
        <option value="">
          Choose a version
        </option>
        <option
          v-for="v in versions"
          :key="v.id"
          :value="v.id"
        >
          v{{ v.version }}
        </option>
      </select>
    </FormField>

    <FormField
      field-id="split"
      label="Split"
      help="Optional. A version with no split is one whose models have no holdout."
    >
      <select
        id="split"
        v-model="splitId"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
        <option value="">
          No split
        </option>
        <option
          v-for="s in splits"
          :key="s.id"
          :value="s.id"
        >
          {{ s.name }} ({{ s.method }})
        </option>
      </select>
    </FormField>

    <FormField
      field-id="family-slug"
      label="Model family slug"
    >
      <input
        id="family-slug"
        v-model="modelFamilySlug"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
    </FormField>

    <FormField
      field-id="response"
      label="Response"
      help="What is being modelled. Required here: the actuarial defaults for it are not
            available to this form, so it is recorded rather than applied."
    >
      <select
        id="response"
        v-model="response"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
        <option value="">
          Choose a response
        </option>
        <option
          v-for="r in RESPONSES"
          :key="r"
          :value="r"
        >
          {{ r }}
        </option>
      </select>
    </FormField>

    <FormField
      field-id="response-column"
      label="Response column"
    >
      <input
        id="response-column"
        v-model="responseColumn"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
    </FormField>

    <FormField
      field-id="offset-kind"
      label="Offset"
    >
      <select
        id="offset-kind"
        v-model="offsetKind"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
        <option value="none">
          None
        </option>
        <option value="log_column">
          log(column)
        </option>
        <option value="column">
          Column
        </option>
      </select>
    </FormField>

    <FormField
      v-if="offsetKind !== 'none'"
      field-id="offset-column"
      label="Offset column"
    >
      <input
        id="offset-column"
        v-model="offsetColumn"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
    </FormField>

    <FormField
      field-id="weight-kind"
      label="Weight"
    >
      <select
        id="weight-kind"
        v-model="weightKind"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
        <option value="none">
          None
        </option>
        <option value="column">
          Column
        </option>
      </select>
    </FormField>

    <FormField
      v-if="weightKind !== 'none'"
      field-id="weight-column"
      label="Weight column"
    >
      <input
        id="weight-column"
        v-model="weightColumn"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
    </FormField>

    <FormField
      field-id="factors"
      label="Factors"
    >
      <select
        id="factors"
        v-model="chosenFactors"
        multiple
        class="h-32 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
        <option
          v-for="f in factors"
          :key="f.id"
          :value="f.id"
        >
          {{ f.slug }}
        </option>
      </select>
    </FormField>

    <div
      role="tablist"
      class="mb-4 flex gap-2 border-b border-slate-200"
    >
      <button
        v-for="a in (['glm', 'gbm', 'ebm'] as const)"
        :key="a"
        type="button"
        role="tab"
        :aria-selected="arm === a"
        :class="['px-3 py-1.5 text-sm', arm === a
          ? 'border-b-2 border-teal-700 font-medium text-teal-800'
          : 'text-slate-600']"
        @click="arm = a"
      >
        {{ a.toUpperCase() }}
      </button>
    </div>

    <template v-if="arm === 'glm'">
      <FormField
        field-id="family"
        label="Family"
      >
        <select
          id="family"
          v-model="family"
          class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
        >
          <option
            v-for="f in FAMILIES"
            :key="f"
            :value="f"
          >
            {{ f }}
          </option>
        </select>
      </FormField>

      <FormField
        field-id="link"
        label="Link"
      >
        <select
          id="link"
          v-model="link"
          class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
        >
          <option
            v-for="l in LINKS"
            :key="l"
            :value="l"
          >
            {{ l }}
          </option>
        </select>
      </FormField>

      <FormField
        v-if="family === 'tweedie'"
        field-id="tweedie-power"
        label="Tweedie power"
        help="Strictly between 1 and 2. At 1 it is Poisson and at 2 it is Gamma."
      >
        <input
          id="tweedie-power"
          v-model.number="tweediePower"
          type="number"
          step="0.1"
          class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
        >
      </FormField>
    </template>

    <template v-else-if="arm === 'gbm'">
      <FormField
        field-id="gbm-backend"
        label="Backend"
      >
        <select
          id="gbm-backend"
          v-model="gbmBackend"
          class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
        >
          <option value="xgboost">
            XGBoost
          </option>
          <option value="lightgbm">
            LightGBM
          </option>
        </select>
      </FormField>

      <FormField
        field-id="gbm-objective"
        label="Objective"
        help="Built-in objectives only in this slice; approved custom objectives follow."
      >
        <select
          id="gbm-objective"
          v-model="gbmObjective"
          class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
        >
          <option
            v-for="o in BUILTIN_GBM_OBJECTIVES"
            :key="o"
            :value="o"
          >
            {{ o }}
          </option>
        </select>
      </FormField>
    </template>

    <template v-else>
      <FormField
        field-id="ebm-objective"
        label="Objective"
      >
        <select
          id="ebm-objective"
          v-model="ebmObjective"
          class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
        >
          <option value="rmse">
            rmse
          </option>
          <option value="mae">
            mae
          </option>
        </select>
      </FormField>
    </template>

    <section
      class="mt-6"
      aria-live="polite"
    >
      <p
        v-if="checking"
        class="text-sm text-slate-500"
      >
        Checking…
      </p>

      <!--
        The 422 arm. Rendered from `errors[]` rather than from `title`/`detail`, because
        the actionable sentence is only there — measured, see the script block.
      -->
      <div
        v-if="fieldErrors.length"
        role="alert"
        class="rounded-md border border-red-200 bg-red-50 p-4"
      >
        <p class="font-medium text-red-900">
          This spec cannot be stored
        </p>
        <ul class="mt-2 space-y-1">
          <li
            v-for="(error, index) in fieldErrors"
            :key="index"
            class="text-sm text-red-800"
          >
            {{ error.message }}
            <span class="ml-1 font-mono text-xs text-red-700">{{ error.field }}</span>
          </li>
        </ul>
        <p
          v-if="problem?.traceId"
          class="mt-2 font-mono text-xs text-red-700"
        >
          trace {{ problem.traceId }}
        </p>
      </div>

      <!-- Every other failure: the 404 for an absent version, and anything else. -->
      <div
        v-else-if="problem"
        role="alert"
        class="rounded-md border border-red-200 bg-red-50 p-4"
      >
        <p class="font-medium text-red-900">
          {{ problem.problem.title }}
        </p>
        <p
          v-if="problem.problem.detail"
          class="mt-1 text-sm text-red-800"
        >
          {{ problem.problem.detail }}
        </p>
        <p
          v-if="problem.traceId"
          class="mt-2 font-mono text-xs text-red-700"
        >
          trace {{ problem.traceId }}
        </p>
      </div>

      <template v-else-if="validation">
        <p
          v-if="validation.ok"
          class="rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-900"
        >
          This spec may be fitted.
        </p>

        <SpecProblemList :problems="validation.problems" />

        <!--
          The complexity block, drawn whenever a validation response has arrived and
          **independent of `ok`** (FR-MODEL-81). Complexity is "a diagnostic by default,
          and a gate only where a workspace asks for one": both limits are unset unless a
          workspace sets them, so in a default workspace no `complexity_limit` problem is
          ever raised and `ok` stays true for a spec with 300 factors on 40 exposure-years.
          A block rendered only when `ok` is false would therefore show the diagnostic
          never — in exactly the configuration the requirement is about.
        -->
        <h2 class="mt-4 text-sm font-medium text-slate-700">
          Complexity
        </h2>
        <dl
          aria-label="Complexity"
          class="mt-1 grid grid-cols-2 gap-2 text-sm"
        >
          <dt class="text-slate-600">
            Factors
          </dt>
          <dd class="tabular-nums">
            {{ validation.factor_count }}
            <span
              v-if="validation.max_factor_count != null"
              class="text-slate-500"
            >/ {{ validation.max_factor_count }}</span>
          </dd>

          <dt class="text-slate-600">
            Estimated parameters
          </dt>
          <dd class="tabular-nums">
            {{ validation.estimated_parameter_count }}
          </dd>

          <template v-if="validation.exposure_per_parameter != null">
            <dt class="text-slate-600">
              Exposure per parameter
            </dt>
            <dd class="tabular-nums">
              {{ validation.exposure_per_parameter.toFixed(1) }}
              <span
                v-if="validation.min_exposure_per_parameter != null"
                class="text-slate-500"
              >/ {{ validation.min_exposure_per_parameter }} minimum</span>
            </dd>
          </template>
        </dl>
      </template>
    </section>
  </section>
</template>
