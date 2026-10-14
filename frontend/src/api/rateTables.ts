import { request } from "./client";
import type { components } from "./generated/schema";
import type { components as requestComponents } from "./generated/schema.requests";
import type { Job } from "./jobs";

export type RateTable = components["schemas"]["RateTable"];
export type RateTableCell = components["schemas"]["RateTableCell"];
export type RateTableCellPage = components["schemas"]["Page_RateTableCell_"];
export type RateTableDiff = components["schemas"]["RateTableDiff"];
export type RateTableVersion = components["schemas"]["RateTableVersion"];
export type RateTableDiffCell = components["schemas"]["RateTableDiffCell"];
export type RateTableDiffCellPage = components["schemas"]["Page_RateTableDiffCell_"];
export type ImportVerdict = components["schemas"]["ImportVerdict"];
/** What `POST …/import` answers (200) while `confirm` is false (03 §5.1); the 201 is a `RateTableVersion`. */
export type ImportPreview = components["schemas"]["ImportPreview"];
/** `GET …/diff/cells` `against`: `previous`, `seed`, or a version number (FR-231). */
export type DiffAgainst = string;
/** A bulk operation's request, discriminated on `kind` (FR-233, `SL-1669`). */
export type BulkOperationRequest =
  | requestComponents["schemas"]["UpliftTableRequest"]
  | requestComponents["schemas"]["UpliftByFilterRequest"]
  | requestComponents["schemas"]["FloorAndCapRequest"]
  | requestComponents["schemas"]["RebaseToLevelRequest"];
/** The edit body without `confirm`: preview and confirm set it, so a caller cannot send both. */
export type RateTableEdit = Omit<requestComponents["schemas"]["RateTableManualEdit"], "confirm">;

/** A version's definition, without its cells (FR-1636). `ref` is `slug@version`. */
export function getRateTable(ref: string): Promise<RateTable> {
  return request<RateTable>(`/rate-tables/${ref}`);
}

/** One page of a version's cells, in key order; the server's cursor does the paging (FR-232). */
export function getCellPage(ref: string, cursor?: string): Promise<RateTableCellPage> {
  return request<RateTableCellPage>(`/rate-tables/${ref}/cells`, {
    query: { cursor },
  });
}

/** The would-be version's diff against its base; nothing is created (FR-229, FR-231). */
export function previewEdit(slug: string, body: RateTableEdit): Promise<RateTableDiff> {
  return request<RateTableDiff>(`/rate-tables/${encodeURIComponent(slug)}/versions`, {
    method: "POST",
    body: { ...body, confirm: false },
  });
}

/** Creates the version the preview showed (FR-229). */
export function confirmEdit(slug: string, body: RateTableEdit): Promise<RateTableVersion> {
  return request<RateTableVersion>(`/rate-tables/${encodeURIComponent(slug)}/versions`, {
    method: "POST",
    body: { ...body, confirm: true },
  });
}

/**
 * One page of the cells that differ from `against`, with the exposure weight behind each when a
 * `portfolio` Dataset Version is named (FR-231). The first request for a key may answer `202`
 * with the Job that builds it (FR-232); the body then is a `Job`, not a page.
 */
export function getDiffCells(
  ref: string,
  query: { against: DiffAgainst; portfolio?: string; cursor?: string },
): Promise<RateTableDiffCellPage | Job> {
  return request<RateTableDiffCellPage | Job>(`/rate-tables/${ref}/diff/cells`, { query });
}

/** A `202` answer is a Job; a page has `items` (FR-232). */
export function isJob(answer: RateTableDiffCellPage | Job): answer is Job {
  return !("items" in answer);
}

/** Applies a bulk operation to a version and creates the next one, recording its parameters (FR-233). */
export function bulkOperation(ref: string, body: BulkOperationRequest): Promise<RateTableVersion> {
  return request<RateTableVersion>(`/rate-tables/${ref}/bulk-operation`, { method: "POST", body });
}

function uploadForm(file: File, confirm: boolean): FormData {
  const form = new FormData();
  form.set("file", file);
  form.set("confirm", String(confirm));
  return form;
}

/** Checks an uploaded CSV against the version and returns the diff it would make; nothing is created (FR-235). */
export function previewImport(ref: string, file: File): Promise<ImportPreview> {
  return request<ImportPreview>(`/rate-tables/${ref}/import`, {
    method: "POST",
    body: uploadForm(file, false),
  });
}

/** Creates the version the same upload previewed (FR-235). */
export function confirmImport(ref: string, file: File): Promise<RateTableVersion> {
  return request<RateTableVersion>(`/rate-tables/${ref}/import`, {
    method: "POST",
    body: uploadForm(file, true),
  });
}

/** The version's cells as CSV text, decimals as strings (FR-235). */
export function exportCsv(ref: string): Promise<string> {
  return request<string>(`/rate-tables/${ref}/export/csv`, { responseType: "text" });
}
