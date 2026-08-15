import { request } from "./client";
import type { components } from "./generated/schema";

export type Model = components["schemas"]["Model"];
export type GlmFitResult = components["schemas"]["GlmFitResult"];
export type Coefficient = components["schemas"]["Coefficient"];
export type RelativityLevel = components["schemas"]["RelativityLevel"];
export type Factor = components["schemas"]["Factor"];

/** The model artifact — latest version, or the one named. */
export function getModel(slug: string, version?: number): Promise<Model> {
  return request<Model>(`/models/${encodeURIComponent(slug)}`, {
    query: { version },
  });
}

/** Factors defined against a dataset, newest version of each first. */
export function listFactors(datasetId?: string): Promise<Factor[]> {
  return request<Factor[]>("/factors", { query: { dataset_id: datasetId } });
}

/**
 * How wide an interval is, as a fraction of the estimate — the number that says whether a
 * coefficient is worth reading.
 *
 * `02` R5 makes uncertainty part of what an estimate *is*, and a table of point estimates
 * invites exactly the reading it exists to prevent: that a relativity of 1.72 on 40 rows
 * and one on 400 000 mean the same thing.
 */
export function intervalWidth(coefficient: Coefficient): number {
  const [low, high] = coefficient.ci_95;
  return high - low;
}

/** A coefficient whose interval spans zero has not been distinguished from no effect. */
export function spansZero(coefficient: Coefficient): boolean {
  const [low, high] = coefficient.ci_95;
  return low <= 0 && high >= 0;
}

/** Relativity intervals, exponentiated for a log link — what the table actually shows. */
export function relativityInterval(coefficient: Coefficient): [number, number] {
  const [low, high] = coefficient.ci_95;
  return [Math.exp(low), Math.exp(high)];
}
