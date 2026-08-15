<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { listVersions } from "@/api/datasets";
import type { DatasetVersion } from "@/api/versions";
import { waitForJob } from "@/api/jobs";
import { ProblemError } from "@/api/problem";
import { createRule, dryRun, LAYERS, submitRule, type ValidationLayer } from "@/api/rules";

const props = defineProps<{ slug: string }>();
const emit = defineEmits<{ (event: "authored"): void }>();

/**
 * FR-DATA-21's chain, in the order the platform enforces it. A rule cannot skip a step:
 * an approver reading a rule's JSON cannot tell whether it selects three rows or three
 * million, which is why the dry run is a precondition of submission rather than advice.
 */
const stage = ref<"idle" | "creating" | "running" | "submitting" | "done">("idle");
const error = ref<string | null>(null);
const versions = ref<DatasetVersion[]>([]);

const form = ref({
  slug: "",
  layer: "actuarial_sanity" as ValidationLayer,
  check: "range",
  severity: "warn" as "warn" | "fail",
  table: "policy_exposure",
  column: "",
  params: "{}",
  rationale: "",
  versionId: "",
});

const busy = computed(() => stage.value !== "idle" && stage.value !== "done");

onMounted(async () => {
  // Caught, not left to reject: an unhandled rejection in a mounted hook leaves a form
  // that looks usable and is not, with nothing on screen saying why.
  try {
    const page = await listVersions(props.slug, { limit: 20 });
    versions.value = page.items ?? [];
    form.value.versionId = versions.value[0]?.id ?? "";
  } catch (caught) {
    if (caught instanceof ProblemError) error.value = caught.problem.title;
    else throw caught;
  }
});

async function author(): Promise<void> {
  error.value = null;
  let params: Record<string, unknown>;
  try {
    params = JSON.parse(form.value.params || "{}") as Record<string, unknown>;
  } catch {
    // Parsed here rather than posted raw: a 422 from the server would name a field the
    // user cannot see, and the fix is in this textarea.
    error.value = "Parameters must be valid JSON.";
    return;
  }

  try {
    stage.value = "creating";
    const rule = await createRule({
      slug: form.value.slug,
      layer: form.value.layer,
      check: form.value.check,
      severity: form.value.severity,
      target: { table: form.value.table, column: form.value.column },
      params,
      rationale: form.value.rationale,
    });

    stage.value = "running";
    const accepted = (await dryRun(rule.id, form.value.versionId)) as { id?: string };
    if (accepted.id) {
      const job = await waitForJob(accepted.id);
      if (job.status !== "succeeded") {
        // Not an error to hide: a rule whose dry run failed is exactly the rule an
        // approver must not be asked to read.
        error.value = `The dry run ${job.status}. The rule stays a draft until it runs.`;
        stage.value = "idle";
        return;
      }
    }

    stage.value = "submitting";
    await submitRule(rule.id);
    stage.value = "done";
    emit("authored");
  } catch (caught) {
    if (caught instanceof ProblemError) {
      error.value = `${caught.problem.title}. ${caught.problem.detail ?? ""}`.trim();
      stage.value = "idle";
    } else throw caught;
  }
}
</script>

<template>
  <form
    class="mt-8 rounded-md border border-slate-200 p-4"
    @submit.prevent="author"
  >
    <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
      New rule
    </h2>
    <p class="mt-1 text-xs text-slate-500">
      Authored as a <strong>draft</strong>, dry-run against a real version, then submitted
      for someone else to approve (FR-DATA-21). Editing an approved rule is not an update —
      reuse its slug and the platform allocates the next version.
    </p>

    <div class="mt-4 grid gap-3 sm:grid-cols-2">
      <label class="text-sm">
        <span class="text-slate-600">Slug</span>
        <input
          v-model="form.slug"
          required
          pattern="[a-z0-9-]+"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
      </label>
      <label class="text-sm">
        <span class="text-slate-600">Layer</span>
        <select
          v-model="form.layer"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
          <option
            v-for="layer in LAYERS"
            :key="layer"
            :value="layer"
          >
            {{ layer.replaceAll("_", " ") }}
          </option>
        </select>
      </label>
      <label class="text-sm">
        <span class="text-slate-600">Check</span>
        <input
          v-model="form.check"
          required
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
      </label>
      <label class="text-sm">
        <span class="text-slate-600">Severity</span>
        <select
          v-model="form.severity"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
          <option value="warn">warn</option>
          <option value="fail">fail</option>
        </select>
      </label>
      <label class="text-sm">
        <span class="text-slate-600">Table</span>
        <input
          v-model="form.table"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
      </label>
      <label class="text-sm">
        <span class="text-slate-600">Column</span>
        <input
          v-model="form.column"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
      </label>
      <label class="text-sm sm:col-span-2">
        <span class="text-slate-600">Parameters (JSON)</span>
        <textarea
          v-model="form.params"
          rows="3"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1 font-mono text-xs"
        />
      </label>
      <label class="text-sm sm:col-span-2">
        <span class="text-slate-600">Rationale</span>
        <input
          v-model="form.rationale"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
      </label>
      <label class="text-sm">
        <span class="text-slate-600">Dry-run against</span>
        <select
          v-model="form.versionId"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
          <option
            v-for="version in versions"
            :key="version.id"
            :value="version.id"
          >
            v{{ version.version }}
          </option>
        </select>
      </label>
    </div>

    <p
      v-if="error"
      role="alert"
      class="mt-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-900"
    >
      {{ error }}
    </p>
    <p
      v-else-if="stage === 'done'"
      class="mt-3 text-sm text-emerald-800"
    >
      Submitted for approval. It cannot enter the rule set until someone other than you
      approves it.
    </p>

    <div class="mt-4 flex items-center gap-3">
      <button
        type="submit"
        :disabled="busy || !versions.length"
        class="rounded bg-slate-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
      >
        Author, dry-run and submit
      </button>
      <span
        v-if="busy"
        class="text-sm text-slate-500"
      >{{ stage === "running" ? "Dry run in progress…" : "Working…" }}</span>
      <span
        v-else-if="!versions.length"
        class="text-sm text-slate-500"
      >A rule can only be submitted once it has run against a real version, and this
        dataset has none yet.</span>
    </div>
  </form>
</template>
