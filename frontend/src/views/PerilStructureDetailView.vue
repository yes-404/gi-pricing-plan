<script setup lang="ts">
/**
 * `02` §5.3's Peril structure detail, `/peril-structures/:id`.
 *
 * **Built from the contract's fields, not from the cell's three nouns.** The cell names
 * per-peril model pins, large-loss treatment and a reconciliation panel — six of the
 * contract's twenty-five fields. Under OQ-587's decided rule the generated contract is
 * the floor and the Contents cell binds nothing, so a field present in `PerilStructure` and
 * absent from the cell is in scope by the contract. Five of the unnamed fields are required by
 * numbered requirements independently of that: `excluded_perils` and `part` by FR-190,
 * `status` by FR-191, `method` by FR-188, `restoration_loading` by FR-128.
 *
 * **Model refs are canonical strings, and are not destructured.** `ArtifactRef` overrides its
 * JSON schema to emit a string, so `frequency_model` arrives as `"model:ad-freq@4"`. That
 * string is the display form — it is what appears in traces and audit rows and what a user
 * pastes into a ticket, so splitting it into "ad-freq (v4)" makes the pinned reference
 * unsearchable against every other surface.
 *
 * **All four large-loss kinds render by name.** `pricing_core` refuses `separate_model` and
 * `flat_loading` at compute time, but the contract has carried all four from the start and
 * FR-207's staged-contract rule makes that intended. A `v-if` over the computable pair
 * would render a blank treatment for a structure that declares one, reading as "no large-loss
 * handling" when the structure says otherwise. The refusal surfaces on the reconcile path.
 *
 * **The reconciliation panel is gated on `status`, not on `reconciliation === null`.** A
 * `draft` structure legitimately has none — the validator requires one only in `reconciled`,
 * `review` and `approved` — so treating the null as a fetch failure shows an error over a
 * perfectly valid draft.
 */
import { onMounted, ref } from "vue";

import { getPerilStructure, type PerilStructure } from "@/api/perils";
import { ProblemError } from "@/api/problem";
import ArtifactStatusBadge from "@/components/ArtifactStatusBadge.vue";
import ReconciliationPanel from "@/components/ReconciliationPanel.vue";

const props = defineProps<{ id: string }>();

const structure = ref<PerilStructure | undefined>(undefined);
const failure = ref<string | undefined>(undefined);

onMounted(async () => {
  try {
    structure.value = await getPerilStructure(props.id);
  } catch (error) {
    failure.value
      = error instanceof ProblemError
        ? (error.problem.detail ?? error.problem.title)
        : String(error);
  }
});
</script>

<template>
  <main class="mx-auto max-w-4xl p-6">
    <p
      v-if="failure"
      role="alert"
      class="rounded bg-amber-50 p-3 text-sm text-amber-900"
    >
      {{ failure }}
    </p>

    <template v-else-if="structure">
      <header>
        <p class="text-xs uppercase tracking-wide text-slate-500">
          Peril structure
        </p>
        <h1 class="mt-1 text-xl font-semibold tracking-tight">
          {{ structure.slug }} v{{ structure.version }}
          <ArtifactStatusBadge
            v-if="structure.status"
            :status="structure.status"
            class="ml-2 align-middle"
          />
        </h1>
        <p class="mt-1 text-sm text-slate-500">
          Created {{ structure.created_at }}.
        </p>
      </header>

      <!-- FR-188: each peril, the method that decides what its refs mean, and the refs
           themselves as canonical strings. -->
      <section class="mt-8">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Composition
        </h2>
        <table class="mt-2 w-full text-left text-sm">
          <thead class="border-b border-slate-200 text-xs uppercase text-slate-500">
            <tr>
              <th
                scope="col"
                class="py-1 font-medium"
              >
                Peril
              </th>
              <th
                scope="col"
                class="py-1 font-medium"
              >
                Method
              </th>
              <th
                scope="col"
                class="py-1 font-medium"
              >
                Models
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="component in structure.perils"
              :key="component.peril"
              class="border-b border-slate-100"
            >
              <td class="py-1">
                {{ component.peril }}
              </td>
              <td class="py-1">
                {{ component.method }}
              </td>
              <td class="py-1">
                <!-- Whichever refs this method makes meaningful. Rendered as the canonical
                     string the wire carries, never split into parts. -->
                <span
                  v-if="component.frequency_model"
                  class="mr-2 font-mono text-xs"
                >{{ component.frequency_model }}</span>
                <span
                  v-if="component.severity_model"
                  class="mr-2 font-mono text-xs"
                >{{ component.severity_model }}</span>
                <span
                  v-if="component.burning_cost_model"
                  class="mr-2 font-mono text-xs"
                >{{ component.burning_cost_model }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- FR-189's treatment and its parameters. The amounts are integer minor units with
           no symbol and no denomination label: a cap and an attachment point are unambiguously
           money, so omitting them would remove requirement content the way omitting the
           burning costs does not — but this view cannot source a currency (OQ-551), so it
           states the contract's own field values and asserts no denomination. -->
      <section class="mt-8">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Large-loss treatment
        </h2>
        <dl class="mt-2 space-y-2 text-sm">
          <div
            v-for="component in structure.perils"
            :key="component.peril"
            class="border-b border-slate-100 pb-2"
          >
            <dt class="inline font-medium">
              {{ component.peril }}:
            </dt>
            <dd class="inline">
              {{ component.large_loss.kind }}
              <template v-if="component.large_loss.cap_minor != null">
                · cap_minor {{ component.large_loss.cap_minor }}
              </template>
              <template v-if="component.large_loss.attachment_minor != null">
                · attachment_minor {{ component.large_loss.attachment_minor }}
              </template>
              <template v-if="component.large_loss.loading_factor != null">
                · loading_factor {{ component.large_loss.loading_factor }}
              </template>
              <template v-if="component.large_loss.excess_model != null">
                · <span class="font-mono text-xs">{{ component.large_loss.excess_model }}</span>
              </template>
              <template v-if="component.large_loss.restoration_loading != null">
                · restoration_loading {{ component.large_loss.restoration_loading }}
              </template>
            </dd>
          </div>
        </dl>
      </section>

      <!-- FR-190: every peril is either modelled or explicitly excluded with a reason.
           Named by no noun in the cell, and required by the requirement. -->
      <section
        v-if="structure.excluded_perils?.length"
        class="mt-8"
      >
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Excluded perils
        </h2>
        <dl class="mt-2 space-y-1 text-sm">
          <div
            v-for="excluded in structure.excluded_perils"
            :key="excluded.peril"
          >
            <dt class="inline font-medium">
              {{ excluded.peril }}:
            </dt>
            <dd class="inline text-slate-600">
              {{ excluded.reason }}
            </dd>
          </div>
        </dl>
      </section>

      <ReconciliationPanel
        v-if="structure.reconciliation"
        :reconciliation="structure.reconciliation"
      />
      <p
        v-else
        class="mt-6 text-sm text-slate-500"
      >
        Not yet reconciled. FR-190 makes the reconciliation the evidence an approver reads,
        and a structure acquires one by being reconciled — a draft having none is an ordinary
        state, not a missing artifact.
      </p>
    </template>
  </main>
</template>
