import { render, screen, within } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { components } from "@/api/generated/schema";
import MetricLibraryView from "../MetricLibraryView.vue";

type CustomMetric = components["schemas"]["CustomMetric"];
type MetricCertificateRead = components["schemas"]["MetricCertificateRead"];

const CERTIFIED: CustomMetric = {
  id: "0b9a6c1e-1111-4222-8333-444455556666",
  slug: "gini-weighted",
  version: 3,
  kind: "template",
  status: "approved",
  direction: "higher_is_better",
  applicability: { responses: ["claim_count"], backends: ["xgboost"], offset_required: false, y_domain: {} },
  usage_count: 2,
  certificate_id: "c3c3c3c3-7777-4888-8999-aaaabbbbcccc",
};

// Never certified: its certificate read is a 404 `NOT_FOUND` (`platform/metrics.py`,
// `load_certificate`), which is an answer and not a failure.
const UNCERTIFIED: CustomMetric = {
  id: "0b9a6c1e-2222-4222-8333-444455556666",
  slug: "capped-deviance",
  version: 1,
  kind: "template",
  status: "draft",
  direction: "lower_is_better",
  applicability: { responses: ["claim_count"], backends: ["xgboost"], offset_required: false, y_domain: {} },
  usage_count: 0,
  certificate_id: null,
};

const CERTIFICATE: MetricCertificateRead = {
  id: "c3c3c3c3-7777-4888-8999-aaaabbbbcccc",
  custom_metric_id: CERTIFIED.id,
  metric_version: 3,
  certified_at: "2026-11-02T10:00:00Z",
  job_id: "9d9d9d9d-1234-4567-8901-abcdefabcdef",
  result: {
    checks: [{ name: "finiteness", status: "pass", detail: "finite throughout" }],
    sampling: { n_points: 1000, seed: 7, y_range: [0, 10], f_range: [-5, 5], w_range: [1, 1] },
    overall: "certified",
  },
  provenance: {
    entity_type: "metric_certificate",
    entity_id: "c3c3c3c3-7777-4888-8999-aaaabbbbcccc",
    produced_by_job_id: "9d9d9d9d-1234-4567-8901-abcdefabcdef",
    subject_refs: ["custom_metric:gini-weighted@3"],
  },
};

const NOT_FOUND = {
  type: "about:blank", title: "Not found", status: 404, code: "NOT_FOUND",
  detail: "This metric has not been certified", errors: [],
};

function stubFetch(
  metrics: CustomMetric[],
  certified: { status: number; body: unknown } = { status: 200, body: CERTIFICATE },
): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn(async (input: unknown) => {
    const path = new URL(String(input), "http://localhost").pathname;
    const json = (body: unknown, status = 200) =>
      new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
    if (path.endsWith(`/custom-metrics/${CERTIFIED.id}/certificate`)) {
      return json(certified.body, certified.status);
    }
    if (path.endsWith("/certificate")) return json(NOT_FOUND, 404);
    if (path.endsWith("/custom-metrics")) return json({ items: metrics, next_cursor: null });
    return json(NOT_FOUND, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

const mounted = { global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } } };

afterEach(() => vi.unstubAllGlobals());

describe("MetricLibraryView", () => {
  it("shows the provenance badge of a certified metric's certificate (FR-2159)", async () => {
    stubFetch([CERTIFIED, UNCERTIFIED]);
    render(MetricLibraryView, mounted);

    const badge = await screen.findByRole("group", { name: "Provenance" });
    expect(within(badge).getByText(CERTIFICATE.provenance.produced_by_job_id!)).toBeInTheDocument();
    expect(badge).toHaveTextContent("custom_metric:gini-weighted@3");
    // One badge: the uncertified metric has no certificate, so it has nothing to show.
    expect(screen.getAllByRole("group", { name: "Provenance" })).toHaveLength(1);
    expect(screen.getByText("capped-deviance")).toBeInTheDocument();
  });

  it("asks for no certificate for a metric without a certificate_id, and shows no badge for it", async () => {
    // Only the current certificate's provenance is shown: `certificate_id` names it.
    const fetchMock = stubFetch([CERTIFIED, UNCERTIFIED]);
    const { container } = render(MetricLibraryView, mounted);

    // The certified metric's badge is the signal that the certificate reads have settled.
    await screen.findByRole("group", { name: "Provenance" });
    const urls = fetchMock.mock.calls.map((c) => String(c[0])).join(" ");
    expect(urls).toContain(`/custom-metrics/${CERTIFIED.id}/certificate`);
    expect(urls).not.toContain(`/custom-metrics/${UNCERTIFIED.id}/certificate`);
    expect(screen.getAllByRole("group", { name: "Provenance" })).toHaveLength(1);
    expect(container.textContent ?? "").not.toMatch(/could not be read|not been certified|not found/i);
  });

  it("reads a 404 on a certificate read as no certificate: no badge, and no error", async () => {
    // `NOT_FOUND` is also what an unknown metric answers (`platform/metrics.py`), e.g. one
    // removed between the list and the read. An answer, not a failure.
    const fetchMock = stubFetch([CERTIFIED], { status: 404, body: NOT_FOUND });
    const { container } = render(MetricLibraryView, mounted);

    expect(await screen.findByText("gini-weighted")).toBeInTheDocument();
    await vi.waitFor(() =>
      expect(fetchMock.mock.calls.map((c) => String(c[0])).join(" ")).toContain(
        `/custom-metrics/${CERTIFIED.id}/certificate`,
      ),
    );
    // Nothing renders on success here, so give the read time to settle before asserting absence.
    await new Promise((resolve) => setTimeout(resolve, 50));
    expect(screen.queryByRole("group", { name: "Provenance" })).toBeNull();
    expect(container.textContent ?? "").not.toMatch(/could not be read|not been certified|not found/i);
  });

  it("keeps the library on screen when a certificate read fails for another reason", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: unknown) => {
        const path = new URL(String(input), "http://localhost").pathname;
        const body = path.endsWith("/certificate")
          ? { type: "about:blank", title: "Internal error", status: 500, code: "INTERNAL", detail: "boom", errors: [] }
          : { items: [CERTIFIED], next_cursor: null };
        return new Response(JSON.stringify(body), {
          status: path.endsWith("/certificate") ? 500 : 200,
          headers: { "Content-Type": "application/json" },
        });
      }),
    );
    render(MetricLibraryView, mounted);

    expect(await screen.findByText(/certificates could not be read/i)).toBeInTheDocument();
    expect(screen.getByText("gini-weighted")).toBeInTheDocument();
    expect(screen.queryByRole("group", { name: "Provenance" })).toBeNull();
  });
});
