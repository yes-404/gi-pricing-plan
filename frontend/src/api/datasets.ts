import { request } from "./client";
import type { components } from "./generated/schema";

export type Dataset = components["schemas"]["Dataset"];
export type DatasetPage = components["schemas"]["Page_Dataset_"];

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
