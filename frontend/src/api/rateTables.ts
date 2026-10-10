import { request } from "./client";
import type { components } from "./generated/schema";
import type { components as requestComponents } from "./generated/schema.requests";

export type RateTable = components["schemas"]["RateTable"];
export type RateTableCell = components["schemas"]["RateTableCell"];
export type RateTableCellPage = components["schemas"]["Page_RateTableCell_"];
export type RateTableDiff = components["schemas"]["RateTableDiff"];
export type RateTableVersion = components["schemas"]["RateTableVersion"];
/** The edit body without `confirm`: preview and confirm set it, so a caller cannot send both. */
export type RateTableEdit = Omit<requestComponents["schemas"]["RateTableManualEdit"], "confirm">;

/** A version's definition, without its cells (FR 9940). `ref` is `slug@version`. */
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
