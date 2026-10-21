import { render, screen, waitFor } from "@testing-library/vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { DislocationRun } from "@/api/dislocationRuns";
import { ProblemError } from "@/api/problem";

import DislocationView from "../DislocationView.vue";

const getDislocationRun = vi.fn();
const getDislocationMovers = vi.fn();
const getRatingVersionByRef = vi.fn();

vi.mock("@/api/dislocationRuns", () => ({
  getDislocationRun: (...args: unknown[]) => getDislocationRun(...args),
  getDislocationMovers: (...args: unknown[]) => getDislocationMovers(...args),
}));
vi.mock("@/api/ratingVersions", () => ({
  getRatingVersionByRef: (...args: unknown[]) => getRatingVersionByRef(...args),
}));
vi.mock("vue-echarts", () => ({
  default: { name: "VChart", props: ["option"], template: "<div data-testid='chart' />" },
}));
const push = vi.fn();
vi.mock("vue-router", () => ({
  RouterLink: { props: ["to"], template: "<a><slot /></a>" },
  useRouter: () => ({ push }),
}));

const RUN: DislocationRun = {
  baseline_ref: "rating_version:motor-gb@26",
  candidate_ref: "rating_version:motor-gb@27",
  portfolio_dataset_version_id: "01a04394-338b-7651-9e42-c73ee70396f8",
  policy_count: 12,
  exposure_years: "12",
  totals: { baseline_premium_minor: 100000, candidate_premium_minor: 110000, change_pct: 10 },
  outcomes: {
    quoted_both: 12,
    quoted_to_declined: 0,
    declined_to_quoted: 0,
    declined_both: 0,
    error: 0,
    zero_baseline: 0,
    negative_baseline: 0,
  },
  distribution: [{ band: "≥ +5%", policies: 12, exposure_share: 1, mean_change_pct: 10 }],
  by_segment: [],
  by_ladder_rung: [],
  errors: [],
};

beforeEach(() => {
  vi.clearAllMocks();
  getRatingVersionByRef.mockResolvedValue({ id: "v1", slug: "motor-gb", version: 27 });
  getDislocationMovers.mockResolvedValue([]);
});

describe("DislocationView", () => {
  it("FR-265: reads the run cited by id and shows it, its totals and its histogram", async () => {
    getDislocationRun.mockResolvedValue(RUN);
    render(DislocationView, { props: { slug: "motor-gb", version: "27", run: "run-1" } });
    await waitFor(() => expect(screen.getByText("rating_version:motor-gb@26")).toBeInTheDocument());
    expect(getDislocationRun).toHaveBeenCalledWith("run-1");
    expect(getDislocationMovers).toHaveBeenCalledWith("run-1");
    expect(screen.getByRole("table", { name: /change distribution/i })).toBeInTheDocument();
    // the run total and the single band's mean change
    expect(screen.getAllByText("10.00%")).toHaveLength(2);
  });

  it("FR-265: with no run cited, asks for an id and reads nothing", async () => {
    render(DislocationView, { props: { slug: "motor-gb", version: "27" } });
    await waitFor(() => expect(screen.getByText(/cite a dislocation run/i)).toBeInTheDocument());
    expect(getDislocationRun).not.toHaveBeenCalled();
  });

  it("FR-265: an unknown run is the platform's problem, shown as an alert", async () => {
    getDislocationRun.mockRejectedValue(
      new ProblemError({ type: "x", title: "Not found", status: 404, code: "NOT_FOUND", detail: "No such run.", errors: [] }),
    );
    render(DislocationView, { props: { slug: "motor-gb", version: "27", run: "nope" } });
    expect(await screen.findByRole("alert")).toHaveTextContent("No such run.");
  });

  it("FR-263: a refused /movers read still shows the rest of the run", async () => {
    getDislocationRun.mockResolvedValue(RUN);
    getDislocationMovers.mockRejectedValue(
      new ProblemError({ type: "x", title: "Forbidden", status: 403, code: "PERMISSION_DENIED", detail: "dataset:read needed.", errors: [] }),
    );
    render(DislocationView, { props: { slug: "motor-gb", version: "27", run: "run-1" } });
    expect(await screen.findByText(/movers could not be loaded/i)).toHaveTextContent("dataset:read needed.");
    expect(screen.getByRole("table", { name: /change distribution/i })).toBeInTheDocument();
  });
});
