import { request } from "./client";
import type { components } from "./generated/schema";
import type { components as requestComponents } from "./generated/schema.requests";

export type RatingAlgorithm = components["schemas"]["RatingAlgorithm"];
export type RatingAlgorithmSaved = components["schemas"]["RatingAlgorithmSaved"];
/** The save body: the permissive generated set, since a defaulted field may be omitted (OQ-655 (c)). */
export type RatingAlgorithmDraft = requestComponents["schemas"]["RatingAlgorithmDraft"];
export type RatingStep = RatingAlgorithmDraft["steps"][number];

export function getRatingAlgorithm(slug: string, version: number): Promise<RatingAlgorithm> {
  return request<RatingAlgorithm>(`/rating-algorithms/${encodeURIComponent(slug)}@${version}`);
}

export function saveRatingAlgorithm(
  body: RatingAlgorithmDraft,
  idempotencyKey: string,
): Promise<RatingAlgorithmSaved> {
  return request<RatingAlgorithmSaved>("/rating-algorithms", {
    method: "POST",
    body,
    idempotencyKey,
  });
}

export type InputContractField = RatingAlgorithmDraft["input_contract"][number];
export type RatingInputType = InputContractField["type"];
export type RoundMode = Extract<RatingStep, { type: "output" }>["rounding"]["mode"];
export type ModelReferenceMode = Extract<RatingStep, { type: "model_call" }>["mode"];
