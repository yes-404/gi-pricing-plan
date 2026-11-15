import { request } from "./client";
import type { components } from "./generated/schema";

export type AuditEventListing = components["schemas"]["AuditEventListing"];
export type AuditPage = components["schemas"]["Page_AuditEventListing_"];
export type ChainVerification = components["schemas"]["ChainVerification"];

/** The query's filters (FR-371). `from` and `to` bound `at`; `q` is free text over justifications. */
export interface AuditFilters {
  readonly actor?: string | undefined;
  readonly entity?: string | undefined;
  readonly action?: string | undefined;
  readonly from?: string | undefined;
  readonly to?: string | undefined;
  readonly q?: string | undefined;
}

/** One page of the log, newest first; the server's cursor does the paging (`00` §5.2). */
export function listAudit(filters: AuditFilters, cursor?: string): Promise<AuditPage> {
  return request<AuditPage>("/audit", { query: { ...filters, cursor } });
}

/**
 * Recomputes the chain. With no range it verifies the whole chain, which is NFR-521's proof;
 * with `from` or `to` it verifies the contiguous span they select (FR-372).
 */
export function verifyChain(range: Pick<AuditFilters, "from" | "to"> = {}): Promise<ChainVerification> {
  return request<ChainVerification>("/audit/verify", { query: { ...range } });
}

/**
 * What the query shows, as a file. JSON Lines is the evidence form an auditor recomputes
 * hashes from; the CSV is a report (`06` §5.1).
 */
export function exportAudit(filters: AuditFilters, format: "csv" | "json"): Promise<string> {
  return request<string>("/audit/export", { query: { ...filters, format }, responseType: "text" });
}

export type ArtifactHistory = components["schemas"]["ArtifactHistory"];
export type ArtifactHistoryEntry = components["schemas"]["ArtifactHistoryEntry"];

/**
 * One artifact version's uniform history (FR-383). `ref` is `{type}:{slug}@{version}`; it is
 * percent-encoded here because its `:` and `@` are not path-safe in every client.
 */
export function getArtifactHistory(ref: string): Promise<ArtifactHistory> {
  return request<ArtifactHistory>(`/artifacts/${encodeURIComponent(ref)}/history`);
}
