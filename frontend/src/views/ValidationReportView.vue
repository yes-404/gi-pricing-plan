<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { ProblemError } from "@/api/problem";
import {
  acknowledge,
  getReport,
  getVersion,
  groupIntoBands,
  listReports,
  type RuleResult,
  type ValidationReport,
} from "@/api/validation";
import AcknowledgeDialog from "@/components/AcknowledgeDialog.vue";
import RuleResultRow from "@/components/RuleResultRow.vue";
import ValidationBanner from "@/components/ValidationBanner.vue";

const props = defineProps<{ slug: string; version: string }>();

const report = ref<ValidationReport | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

const pending = ref<RuleResult | null>(null);
const submitting = ref(false);
const dialogError = ref<string | null>(null);

const bands = computed(() => (report.value ? groupIntoBands(report.value) : null));

/**
 * `01` §5.3's four layer sections, used to organise the tail only. Urgency wins above the
 * fold; a reader asking "why can I not fit a model on this?" needs the blocking rules
 * first, and a failing structural rule blocks exactly as hard as a failing actuarial one.
 */
const LAYERS = ["structural", "referential", "actuarial_sanity", "distributional"] as const;

const otherByLayer = computed(() => {
  const rest = bands.value?.other ?? [];
  return LAYERS.map((layer) => ({
    layer,
    results: rest.filter((result) => result.layer === layer),
  })).filter((section) => section.results.length > 0);
});

async function load(): Promise<void> {
  loading.value = true;
  problem.value = null;
  try {
    const version = await getVersion(props.slug, Number(props.version));
    const history = await listReports(version.id);
    const latest = history[0];
    report.value = latest ? await getReport(latest.id) : null;
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
}

async function confirmAcknowledgement(justification: string): Promise<void> {
  const target = pending.value;
  if (!target || !report.value) return;
  submitting.value = true;
  dialogError.value = null;
  try {
    await acknowledge(report.value.id, target.rule_id, justification);
    pending.value = null;
    // Re-read rather than patch locally: the acknowledgement is recorded server-side with
    // a timestamp and a user, and a client-side copy would be a second version of a fact
    // the audit log owns.
    await load();
  } catch (error) {
    dialogError.value =
      error instanceof ProblemError
        ? `${error.problem.title}. ${error.problem.detail ?? ""}`.trim()
        : "The acknowledgement could not be recorded.";
  } finally {
    submitting.value = false;
  }
}

onMounted(() => void load());
</script>

<template>
  <section>
    <header class="mb-5">
      <p class="text-sm text-slate-500">
        <RouterLink
          to="/data"
          class="hover:underline"
        >
          Datasets
        </RouterLink>
        <span class="mx-1.5">/</span>{{ slug }}<span class="mx-1.5">/</span>v{{ version }}
      </p>
      <h1 class="mt-1 text-xl font-semibold tracking-tight">
        Validation report
      </h1>
    </header>

    <p
      v-if="loading"
      class="text-sm text-slate-500"
    >
      Loading…
    </p>

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

    <p
      v-else-if="!report"
      class="text-sm text-slate-500"
    >
      This version has not been validated yet.
    </p>

    <template v-else-if="bands">
      <ValidationBanner :report="report" />

      <section
        v-if="bands.blocking.length"
        class="mt-8"
      >
        <h2 class="text-sm font-semibold uppercase tracking-wide text-red-800">
          Blocking — {{ bands.blocking.length }}
        </h2>
        <RuleResultRow
          v-for="result in bands.blocking"
          :key="result.rule_id"
          :result="result"
        />
      </section>

      <section
        v-if="bands['needs-acknowledgement'].length"
        class="mt-8"
      >
        <h2 class="text-sm font-semibold uppercase tracking-wide text-amber-800">
          Needs acknowledgement — {{ bands["needs-acknowledgement"].length }}
        </h2>
        <RuleResultRow
          v-for="result in bands['needs-acknowledgement']"
          :key="result.rule_id"
          :result="result"
          @acknowledge="pending = $event"
        />
      </section>

      <section
        v-if="bands.acknowledged.length"
        class="mt-8"
      >
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-600">
          Acknowledged — {{ bands.acknowledged.length }}
        </h2>
        <RuleResultRow
          v-for="result in bands.acknowledged"
          :key="result.rule_id"
          :result="result"
        />
      </section>

      <section
        v-for="section in otherByLayer"
        :key="section.layer"
        class="mt-8"
      >
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          {{ section.layer.replace("_", " ") }} — {{ section.results.length }}
        </h2>
        <RuleResultRow
          v-for="result in section.results"
          :key="result.rule_id"
          :result="result"
        />
      </section>
    </template>

    <AcknowledgeDialog
      :result="pending"
      :submitting="submitting"
      :error="dialogError"
      @cancel="pending = null"
      @confirm="confirmAcknowledgement"
    />
  </section>
</template>
