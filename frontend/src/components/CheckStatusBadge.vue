<script setup lang="ts">
/**
 * §4.7's four-value `CheckStatus`, as a badge.
 *
 * **FR-MODEL-43 as amended 2026-08-25: `violated` is a finding, not a failure.** That is why
 * its label is the word "finding" and its tone is the same family as `warn` rather than
 * `failed`'s. A legitimate non-convex pricing loss produces `violated` on a certificate that
 * is otherwise fine, and a red badge saying "violated" is read as a broken objective by every
 * approver who has not read §4.7.
 *
 * **The rule is on the status, not on the check that emits it.** `violated` comes only from
 * the convexity check today, but `CheckStatus` is a free enum and `outcome_of` branches on the
 * status alone; nothing here asks which check carried it.
 *
 * The label is text, not colour alone — WCAG 1.4.1, and the same reason `StatusBadge` renders
 * its status as a word.
 *
 * Typed on `CheckStatus` and mapped with an exhaustive `Record`, following `StatusBadge`: a
 * map typed on the union cannot omit a member, so a fifth status is a compile error here
 * rather than an unstyled badge in production.
 */
import type { components } from "@/api/generated/schema";

type CheckStatus = components["schemas"]["CheckStatus"];

defineProps<{ status: CheckStatus }>();

const LABEL: Record<CheckStatus, string> = {
  pass: "pass",
  warn: "finding",
  violated: "finding",
  failed: "failed",
};

const TONE: Record<CheckStatus, string> = {
  pass: "bg-emerald-100 text-emerald-800",
  warn: "bg-amber-100 text-amber-900",
  violated: "bg-amber-100 text-amber-900",
  failed: "bg-rose-100 text-rose-900",
};
</script>

<template>
  <span :class="['rounded px-2 py-0.5 text-xs font-medium', TONE[status]]">{{ LABEL[status] }}</span>
</template>
