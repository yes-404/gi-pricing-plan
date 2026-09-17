import { afterEach, describe, expect, it, vi } from "vitest";

import { getDiagnostics, partitions, weightingLabel } from "@/api/diagnostics";
import { DIAGNOSTICS } from "@/views/__tests__/fixtures";

afterEach(() => vi.unstubAllGlobals());

function stub(): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn(
    async () =>
      new Response(JSON.stringify(DIAGNOSTICS), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

/**
 * `client.ts:31` builds `new URL(path, window.location.origin)`, so what reaches `fetch` is
 * always absolute — under jsdom, `http://localhost:3000/...`. Asserting the relative path
 * against the whole URL can never pass. The origin is jsdom configuration and not this
 * module's behaviour, so it is dropped here rather than written into every expectation, and
 * `search` is kept so the version query stays exactly asserted.
 */
function pathOf(fetchMock: ReturnType<typeof vi.fn>): string {
  const url = new URL(String(fetchMock.mock.calls[0]?.[0]));
  return `${url.pathname}${url.search}`;
}

describe("getDiagnostics", () => {
  it("omits the version query when no version is asked for", async () => {
    const fetchMock = stub();
    await getDiagnostics("motor-frequency");
    expect(pathOf(fetchMock)).toBe("/api/v1/models/motor-frequency/diagnostics");
  });

  it("sends the version it was given", async () => {
    const fetchMock = stub();
    await getDiagnostics("motor-frequency", 3);
    expect(pathOf(fetchMock)).toBe("/api/v1/models/motor-frequency/diagnostics?version=3");
  });

  it("percent-encodes a slug", async () => {
    const fetchMock = stub();
    await getDiagnostics("a b");
    expect(pathOf(fetchMock)).toBe("/api/v1/models/a%20b/diagnostics");
  });
});

describe("partitions", () => {
  it("returns train first and holdout second, labelled", () => {
    const pair = partitions(DIAGNOSTICS.universal);
    expect(pair.map(([label]) => label)).toEqual(["Train", "Holdout"]);
    expect(pair[0]?.[1]).toBe(DIAGNOSTICS.universal.train);
    expect(pair[1]?.[1]).toBe(DIAGNOSTICS.universal.holdout);
  });
});

describe("weightingLabel", () => {
  it("names each weighting in the words FR-184 asks the UI to use", () => {
    expect(weightingLabel("exposure")).toBe("exposure-weighted");
    expect(weightingLabel("claim_count")).toBe("claim-count-weighted");
    expect(weightingLabel("count")).toBe("unweighted (row count)");
  });

  it("falls back to the raw value rather than inventing a reading", () => {
    expect(weightingLabel("something_new")).toBe("something_new");
  });
});
