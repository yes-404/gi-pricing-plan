import { request } from "./client";
import type { components } from "./generated/schema";
import type { components as requestComponents } from "./generated/schema.requests";

export type Dataset = components["schemas"]["Dataset"];
export type DatasetStatus = components["schemas"]["DatasetStatus"];
export type DatasetPage = components["schemas"]["Page_Dataset_"];
export type VersionPage = components["schemas"]["Page_DatasetVersion_"];
export type DataDictionaryEntry = components["schemas"]["DataDictionaryEntry"];
// The dictionary **write** takes the permissive entry (OQ-655 (c)): `description` and
// `pii_class` carry defaults a request may omit. Reads keep the strict `DataDictionaryEntry`.
export type RequestDataDictionaryEntry = requestComponents["schemas"]["DataDictionaryEntry"];
export type PiiClass = components["schemas"]["PiiClass"];

/**
 * `01` §5.1 `GET /datasets`.
 *
 * `cursor` is **opaque** — pass back what the last page returned and never parse it. There
 * is no page number, because a dataset created while someone is paging would otherwise
 * make them see one row twice and miss another.
 */
export function listDatasets(options: {
  cursor?: string | undefined;
  limit?: number | undefined;
  lineOfBusiness?: string | undefined;
} = {}): Promise<DatasetPage> {
  return request<DatasetPage>("/datasets", {
    query: {
      cursor: options.cursor,
      limit: options.limit,
      line_of_business: options.lineOfBusiness,
    },
  });
}

export function getDataset(slug: string): Promise<Dataset> {
  return request<Dataset>(`/datasets/${encodeURIComponent(slug)}`);
}

/** The version timeline, newest first (`01` §5.3). */
export function listVersions(
  slug: string,
  options: { cursor?: string | undefined; limit?: number | undefined } = {},
): Promise<VersionPage> {
  return request<VersionPage>(`/datasets/${encodeURIComponent(slug)}/versions`, {
    query: { cursor: options.cursor, limit: options.limit },
  });
}

/**
 * Replace the Data Dictionary (audited, before and after — NFR-472).
 *
 * A **replace**, not a merge: the dictionary decides which columns may be modelled at all
 * (FR-12), so "who removed the special-category marking from this column?" must be
 * answerable — and a merge would make a removal indistinguishable from an omission.
 */
export function putDictionary(
  slug: string,
  entries: Record<string, RequestDataDictionaryEntry>,
): Promise<Dataset> {
  return request<Dataset>(`/datasets/${encodeURIComponent(slug)}/dictionary`, {
    method: "PUT",
    body: { data_dictionary: entries },
  });
}

export type DatasetLineage = components["schemas"]["DatasetLineage"];

export function getLineage(versionId: string): Promise<DatasetLineage> {
  return request<DatasetLineage>(`/dataset-versions/${versionId}/lineage`);
}

/**
 * The classes FR-12 and FR-39 refuse for modelling.
 *
 * Shown as a refusal rather than a warning, because that is what the platform does: a
 * column marked either of these cannot be fitted on, and a UI that presented it as advice
 * would be describing a different system.
 */
export const MODELLING_FORBIDDEN: readonly PiiClass[] = [
  "direct_identifier",
  "special_category",
];

export function forbidsModelling(entry: DataDictionaryEntry | undefined): boolean {
  return entry?.pii_class ? MODELLING_FORBIDDEN.includes(entry.pii_class) : false;
}
