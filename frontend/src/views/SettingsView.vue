<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { ProblemError } from "@/api/problem";
import {
  listSettings,
  updateSetting,
  type SettingResolution,
  type SettingScope,
  type SettingSource,
} from "@/api/settings";

// FR-446 (`07` §3.8, §5.3): the effective value of each setting, with its resolution source
// and constraints. Everything shown comes from the generated resolution; the view holds no
// copy of the settings registry.

const SOURCE_LABEL: Record<SettingSource, string> = {
  env: "Environment variable (GIP_SETTING_<KEY>)",
  environment_setting: "Environment setting",
  workspace: "Workspace setting",
  default: "Platform default",
};

const SCOPE_LABEL: Record<SettingScope, string> = {
  workspace: "Workspace only",
  workspace_or_environment: "Workspace or Environment",
  environment: "Environment only",
};

const settings = ref<SettingResolution[]>([]);
const loading = ref(true);
const loadProblem = ref<ProblemError | null>(null);

const editing = ref<string | null>(null);
const draft = ref<string | number | boolean>("");
const saving = ref(false);
// A row's refusal, keyed by the setting's key. The server's `detail` is shown as it is.
const rowErrors = ref<Record<string, ProblemError>>({});
// A row's refusal of its own draft, made before any request: the draft of a number setting
// that is empty, only whitespace or not a number. The text is fixed; it is never the server's.
const draftRefusals = ref<Record<string, string>>({});

const NOT_A_NUMBER = "Enter a number. Nothing was saved.";

const sorted = computed(() => [...settings.value].sort((a, b) => a.key.localeCompare(b.key)));

/** A value as text. `null` is a layer saying nothing; it is never shown as a value. */
function show(value: unknown): string {
  if (value === null || value === undefined) return "—";
  return typeof value === "string" ? value : JSON.stringify(value);
}

/**
 * Whether this row may be edited here. A value from the process environment outranks every
 * stored layer, and an Environment-only setting takes no workspace-level write (FR-446):
 * the PUT would be refused, so the control is not offered.
 */
function editable(setting: SettingResolution): boolean {
  return setting.resolved_from !== "env" && setting.scope !== "environment";
}

function startEdit(setting: SettingResolution): void {
  editing.value = setting.key;
  const current = setting.effective_value;
  draft.value =
    setting.type === "bool" ? current === true : current === null || current === undefined ? "" : (current as string | number);
  delete rowErrors.value[setting.key];
  delete draftRefusals.value[setting.key];
}

function cancel(): void {
  if (editing.value !== null) delete draftRefusals.value[editing.value];
  editing.value = null;
}

function isNumeric(setting: SettingResolution): boolean {
  return setting.type === "int" || setting.type === "float";
}

/**
 * The draft of a number setting as a number, or `null` when it is not one. `Number("")` and
 * `Number("  ")` are 0, and an emptied `v-model.number` input holds `""`, so a cleared field
 * would otherwise be sent as 0: a value that is in range for a minimum of 0 and is not what
 * the person typed. Only a finite number is a number here.
 */
function numberDraft(): number | null {
  const value = draft.value;
  if (typeof value === "number") return Number.isFinite(value) ? value : null;
  if (typeof value !== "string" || value.trim() === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

/** The draft in the setting's declared type. Whether it is in range is the server's to say. */
function submitted(setting: SettingResolution): unknown {
  if (setting.type === "bool") return draft.value === true;
  if (isNumeric(setting)) return numberDraft();
  return String(draft.value);
}

async function save(setting: SettingResolution): Promise<void> {
  delete rowErrors.value[setting.key];
  delete draftRefusals.value[setting.key];
  // Refused here, before any request: a draft that is not a number is not sent as 0 or NaN.
  if (isNumeric(setting) && numberDraft() === null) {
    draftRefusals.value[setting.key] = NOT_A_NUMBER;
    return;
  }
  saving.value = true;
  try {
    settings.value = await updateSetting(setting.key, submitted(setting));
    editing.value = null;
  } catch (error) {
    if (!(error instanceof ProblemError)) throw error;
    rowErrors.value[setting.key] = error;
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  try {
    settings.value = await listSettings();
  } catch (error) {
    if (!(error instanceof ProblemError)) throw error;
    loadProblem.value = error;
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section>
    <h1 class="text-xl font-semibold tracking-tight">
      Settings
    </h1>
    <p class="mt-1 text-sm text-slate-600">
      Each setting's effective value, the layer that supplied it, and what every layer offered.
      A value from the process environment cannot be changed here.
    </p>

    <p
      v-if="loading"
      class="mt-6 text-sm text-slate-500"
    >
      Loading settings…
    </p>

    <div
      v-if="loadProblem"
      role="alert"
      class="mt-6 rounded-md border border-red-200 bg-red-50 p-4"
    >
      <p class="font-medium text-red-900">
        {{ loadProblem.problem.title }}
      </p>
      <p
        v-if="loadProblem.problem.detail"
        class="mt-1 text-sm text-red-800"
      >
        {{ loadProblem.problem.detail }}
      </p>
      <p
        v-if="loadProblem.traceId"
        class="mt-2 font-mono text-xs text-red-700"
      >
        trace {{ loadProblem.traceId }}
      </p>
    </div>

    <table
      v-if="!loading && !loadProblem"
      class="mt-6 w-full text-left text-sm"
    >
      <caption class="sr-only">
        Effective settings
      </caption>
      <thead>
        <tr class="border-b border-slate-200 text-xs uppercase text-slate-500">
          <th class="py-2 pr-4">
            Setting
          </th>
          <th class="py-2 pr-4">
            Effective value
          </th>
          <th class="py-2 pr-4">
            Source
          </th>
          <th class="py-2 pr-4">
            Scope
          </th>
          <th class="py-2 pr-4">
            Layers
          </th>
          <th class="py-2">
            <span class="sr-only">Actions</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="setting in sorted"
          :key="setting.key"
          class="border-b border-slate-100 align-top"
        >
          <td class="py-3 pr-4">
            <span class="font-mono">{{ setting.key }}</span>
            <span
              v-if="setting.feature_flag"
              class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-600"
            >flag</span>
            <p
              v-if="setting.description"
              class="mt-1 text-xs text-slate-500"
            >
              {{ setting.description }}
            </p>
            <p class="mt-1 text-xs text-slate-500">
              {{ setting.type }}<template v-if="Object.keys(setting.constraints ?? {}).length">
                , {{ show(setting.constraints) }}
              </template>
            </p>
          </td>
          <td class="py-3 pr-4 font-mono">
            <template v-if="editing === setting.key">
              <select
                v-if="setting.type === 'bool'"
                v-model="draft"
                :aria-label="`Value of ${setting.key}`"
                class="rounded border border-slate-300 px-2 py-1"
              >
                <option :value="true">
                  true
                </option>
                <option :value="false">
                  false
                </option>
              </select>
              <input
                v-else-if="setting.type === 'int' || setting.type === 'float'"
                v-model.number="draft"
                type="number"
                :step="setting.type === 'int' ? 1 : 'any'"
                :aria-label="`Value of ${setting.key}`"
                class="w-32 rounded border border-slate-300 px-2 py-1"
              >
              <input
                v-else
                v-model="draft"
                type="text"
                :aria-label="`Value of ${setting.key}`"
                class="w-48 rounded border border-slate-300 px-2 py-1"
              >
            </template>
            <template v-else>
              {{ show(setting.effective_value) }}
            </template>
          </td>
          <td class="py-3 pr-4">
            {{ SOURCE_LABEL[setting.resolved_from] }}
          </td>
          <td class="py-3 pr-4">
            {{ SCOPE_LABEL[setting.scope] }}
          </td>
          <td class="py-3 pr-4">
            <ul class="text-xs text-slate-600">
              <li
                v-for="candidate in setting.candidates"
                :key="candidate.source"
              >
                {{ SOURCE_LABEL[candidate.source] }}:
                <span class="font-mono">{{ show(candidate.value) }}</span>
              </li>
            </ul>
          </td>
          <td class="py-3">
            <template v-if="editing === setting.key">
              <button
                type="button"
                class="mr-2 rounded bg-slate-900 px-2 py-1 text-xs text-white disabled:opacity-50"
                :disabled="saving"
                @click="save(setting)"
              >
                Save
              </button>
              <button
                type="button"
                class="rounded border border-slate-300 px-2 py-1 text-xs"
                @click="cancel"
              >
                Cancel
              </button>
            </template>
            <button
              v-else-if="editable(setting)"
              type="button"
              class="rounded border border-slate-300 px-2 py-1 text-xs"
              @click="startEdit(setting)"
            >
              Edit
            </button>
            <p
              v-if="draftRefusals[setting.key]"
              role="alert"
              class="mt-2 max-w-xs rounded border border-red-200 bg-red-50 p-2 text-xs text-red-800"
            >
              {{ draftRefusals[setting.key] }}
            </p>
            <p
              v-if="rowErrors[setting.key]"
              role="alert"
              class="mt-2 max-w-xs rounded border border-red-200 bg-red-50 p-2 text-xs text-red-800"
            >
              {{ rowErrors[setting.key]!.problem.detail ?? rowErrors[setting.key]!.problem.title }}
            </p>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
