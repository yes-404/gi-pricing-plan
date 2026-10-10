import { computed, onBeforeUnmount, ref, toValue, watch, type MaybeRefOrGetter } from "vue";

import {
  validateRatingAlgorithm,
  type RatingAlgorithmDraft,
  type ValidationIssue,
} from "@/api/ratingAlgorithms";

/**
 * Live validation of the draft on the designer's nodes (03 FR-1607, FR-24). The server owns
 * every graph rule; this only debounces the draft to the validate route, drops a stale call
 * and groups the issues it was handed. Nothing here inspects the draft's content.
 */
export function useGraphValidation(draft: MaybeRefOrGetter<RatingAlgorithmDraft>, delayMs = 400) {
  const issues = ref<ValidationIssue[]>([]);
  const pending = ref(false);

  let timer: ReturnType<typeof setTimeout> | undefined;
  let controller: AbortController | undefined;
  let sequence = 0;

  function cancel(): void {
    clearTimeout(timer);
    controller?.abort();
  }

  watch(
    () => toValue(draft),
    (body) => {
      cancel();
      pending.value = true;
      sequence += 1;
      const mine = sequence;
      timer = setTimeout(() => {
        controller = new AbortController();
        validateRatingAlgorithm(body, controller.signal)
          .then((report) => {
            if (mine !== sequence) return;
            issues.value = report.issues;
            pending.value = false;
          })
          .catch((error: unknown) => {
            if (error instanceof DOMException && error.name === "AbortError") return;
            if (mine !== sequence) return;
            pending.value = false;
          });
      }, delayMs);
    },
    { deep: true, immediate: true },
  );

  onBeforeUnmount(() => {
    sequence += 1;
    cancel();
  });

  const byStep = computed(() => {
    const grouped = new Map<string, ValidationIssue[]>();
    for (const issue of issues.value) {
      if (issue.step_id === null || issue.step_id === undefined) continue;
      grouped.set(issue.step_id, [...(grouped.get(issue.step_id) ?? []), issue]);
    }
    return grouped;
  });
  const graphLevel = computed(() => issues.value.filter((i) => i.step_id == null));

  return { issues, pending, byStep, graphLevel };
}
