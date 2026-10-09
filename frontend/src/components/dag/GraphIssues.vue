<script setup lang="ts">
import type { ValidationIssue } from "@/api/ratingAlgorithms";

defineProps<{ issues: ValidationIssue[]; pending: boolean }>();
</script>

<template>
  <section
    role="status"
    aria-label="Graph issues"
    class="text-sm"
  >
    <p
      v-if="pending"
      class="text-slate-500"
    >
      Checking the graph…
    </p>
    <ul
      v-if="issues.length > 0"
      class="mt-1 space-y-1"
    >
      <li
        v-for="(issue, i) in issues"
        :key="`${issue.code}-${i}`"
        class="rounded border border-red-700 bg-red-50 px-2 py-1 text-red-900"
      >
        <span class="font-medium">Graph issue:</span> {{ issue.message }}
        <span class="ml-1 font-mono text-xs">{{ issue.code }}</span>
      </li>
    </ul>
  </section>
</template>
