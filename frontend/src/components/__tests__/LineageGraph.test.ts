import { render, screen } from "@testing-library/vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { nextTick } from "vue";

import { cellUnder } from "@/test-tables";

import LineageGraph from "../LineageGraph.vue";

vi.mock("vue-echarts", () => ({
  default: { template: "<div data-testid=\"chart\" />", props: ["option"] },
}));

/**
 * happy-dom's `ResizeObserver` never reports. A browser's reports each observed box once,
 * asynchronously, as soon as it is observed, and again whenever its size changes. This one
 * reports `boxSize` once per `observe`, in a microtask, which is all the component reads.
 */
let boxSize = { width: 600, height: 320 };

class ReportingResizeObserver {
  #connected = true;
  constructor(private readonly callback: ResizeObserverCallback) {}
  observe(target: Element) {
    const contentRect = { ...boxSize };
    queueMicrotask(() => {
      if (!this.#connected) return;
      const entry = { target, contentRect } as unknown as ResizeObserverEntry;
      this.callback([entry], this as unknown as ResizeObserver);
    });
  }
  unobserve() {}
  disconnect() {
    this.#connected = false;
  }
}

beforeEach(() => {
  boxSize = { width: 600, height: 320 };
  vi.stubGlobal("ResizeObserver", ReportingResizeObserver);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

const LINEAGE = {
  version_id: "11111111-1111-4111-8111-111111111111",
  built_from: {
    parent_version_id: "22222222-2222-4222-8222-222222222222",
    operation: "sample",
    parameters: {},
  },
  depends_on_this: {
    derived_versions: [
      { version_id: "33333333-3333-4333-8333-333333333333", version: 3, operation: "split" },
    ],
    models: [
      { model_id: "44444444-4444-4444-8444-444444444444", slug: "motor-freq-2026", status: "approved" },
    ],
    rating_versions: [],
    monitoring_baselines: [],
  },
};

describe("the lineage graph", () => {
  it("renders a chart and a table that says what the chart says", async () => {
    render(LineageGraph, { props: { lineage: LINEAGE, version: 2 } });
    expect(await screen.findByTestId("chart")).toBeTruthy();
    const table = screen.getByRole("table", { name: "Lineage" });
    expect(table).toHaveTextContent("v2");
    expect(table).toHaveTextContent("v3");
    expect(table).toHaveTextContent("motor-freq-2026");
    expect(table).toHaveTextContent("approved");
    expect(table).toHaveTextContent("sample");
  });

  it("NFR-463: puts each lineage field under its own heading, read by label", () => {
    render(LineageGraph, { props: { lineage: LINEAGE, version: 2 } });
    const table = screen.getByRole("table", { name: "Lineage" });
    expect(cellUnder(table, /^Built from/, "Operation")).toHaveTextContent("sample");
    expect(cellUnder(table, /^Derived version/, "Name")).toHaveTextContent("v3");
    expect(cellUnder(table, /^Derived version/, "Operation")).toHaveTextContent("split");
    expect(cellUnder(table, /^Model/, "Name")).toHaveTextContent("motor-freq-2026");
    expect(cellUnder(table, /^Model/, "Status")).toHaveTextContent("approved");
    expect(cellUnder(table, /^Model/, "Operation")).toHaveTextContent("—");
  });

  it("renders a single node when nothing depends on the version", () => {
    render(LineageGraph, {
      props: {
        lineage: {
          version_id: "11111111-1111-4111-8111-111111111111",
          built_from: null,
          depends_on_this: {
            derived_versions: [],
            models: [],
            rating_versions: [],
            monitoring_baselines: [],
          },
        },
        version: 1,
      },
    });
    const table = screen.getByRole("table", { name: "Lineage" });
    expect(table).toHaveTextContent("v1");
    expect(table).not.toHaveTextContent("v3");
  });
});

/**
 * #1796: with the real `vue-echarts` and ECharts, not the stub above.
 *
 * The stub is the rule for chart tests here (dev-commands, "vitest exits 1 while printing
 * every test as passed"), and it is why the suite never saw this: the `TypeError` is thrown
 * inside ECharts' graph coordinate system, which only the real library runs.
 *
 * The condition is the one the exit demo logged: "Can't get DOM width or height" one second
 * before the rejection, a chart container with no size. happy-dom gives every element a
 * `clientWidth` and `clientHeight` of 0, but it reports an unresolved `100%` as the computed
 * width and height, and zrender (`canvas/helper.js` `getSize`) falls back to
 * `parseInt("100%")`, a 100 x 100 chart: on its own, happy-dom never produces the zero size.
 * A browser reports a collapsed box as `0px`. The stylesheet below makes happy-dom say the
 * same, and the `ResizeObserver` above reports the same size, which together are the whole of
 * the container each case mounts in.
 *
 * happy-dom has no canvas: `getContext` returns null, and zrender's paint loop and ECharts'
 * text measurement would then throw `TypeError`s of their own, which are not #1796. A no-op 2D
 * context keeps any error this test sees to the one under test.
 */
describe("the lineage graph on the real ECharts (#1796)", () => {
  type NodeProcess = {
    on(event: "unhandledRejection" | "uncaughtException", listener: (reason: unknown) => void): void;
    off(event: "unhandledRejection" | "uncaughtException", listener: (reason: unknown) => void): void;
  };
  // The app tsconfig carries no Node types; the test runs in Node, so `process` is there.
  const nodeProcess = (globalThis as unknown as { process: NodeProcess }).process;

  const noop2dContext = (): CanvasRenderingContext2D => {
    const gradient = { addColorStop: () => undefined };
    const methods: Record<string, unknown> = {
      measureText: (text: string) => ({ width: text.length * 6 }),
      createLinearGradient: () => gradient,
      createRadialGradient: () => gradient,
      createPattern: () => ({}),
      getImageData: () => ({ data: new Uint8ClampedArray(4) }),
      getLineDash: () => [],
    };
    return new Proxy(methods, {
      get: (target, key: string) => (key in target ? target[key] : () => undefined),
      set: (target, key: string, value) => {
        target[key] = value;
        return true;
      },
    }) as unknown as CanvasRenderingContext2D;
  };

  const describeError = (error: unknown): string => {
    if (!(error instanceof Error)) return String(error);
    const frames = (error.stack ?? "").split("\n").slice(1, 6).map((l) => l.trim());
    return [`${error.name}: ${error.message}`, ...frames].join("\n  ");
  };

  const caught: unknown[] = [];
  const onNodeError = (reason: unknown) => caught.push(reason);
  const onWindowError = (event: ErrorEvent) => caught.push(event.error ?? event.message);
  const onWindowRejection = (event: PromiseRejectionEvent) => caught.push(event.reason);
  let sizeSheet: HTMLStyleElement | null = null;

  afterEach(() => {
    nodeProcess.off("unhandledRejection", onNodeError);
    nodeProcess.off("uncaughtException", onNodeError);
    window.removeEventListener("error", onWindowError);
    window.removeEventListener("unhandledrejection", onWindowRejection);
    caught.length = 0;
    sizeSheet?.remove();
    sizeSheet = null;
    vi.restoreAllMocks();
    vi.doMock("vue-echarts", () => ({
      default: { template: "<div data-testid=\"chart\" />", props: ["option"] },
    }));
  });

  /** Mounts the graph on the real library in a box of the given size; returns what it threw. */
  async function mountInBox(width: number, height: number) {
    boxSize = { width, height };
    sizeSheet = document.createElement("style");
    sizeSheet.textContent =
      `x-vue-echarts, x-vue-echarts > .echarts-host ` +
      `{ width: ${width}px !important; height: ${height}px !important; }`;
    document.head.appendChild(sizeSheet);
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockImplementation(
      noop2dContext as unknown as HTMLCanvasElement["getContext"],
    );
    nodeProcess.on("unhandledRejection", onNodeError);
    nodeProcess.on("uncaughtException", onNodeError);
    window.addEventListener("error", onWindowError);
    window.addEventListener("unhandledrejection", onWindowRejection);

    vi.doUnmock("vue-echarts");
    vi.resetModules();
    const { default: RealLineageGraph } = await import("../LineageGraph.vue");

    const { container, unmount } = render(RealLineageGraph, {
      props: { lineage: LINEAGE, version: 2 },
    });
    // The box's size arrives in a microtask, vue-echarts with `autoresize` applies the option
    // in a `nextTick`, and ECharts paints on an animation frame: let all of them run, and Node
    // report any rejection nothing awaited.
    await nextTick();
    await new Promise((resolve) => setTimeout(resolve, 100));
    expect(screen.getByRole("table", { name: "Lineage" })).toHaveTextContent("motor-freq-2026");
    const chartCreated = container.querySelector("x-vue-echarts canvas") !== null;
    unmount();
    return { chartCreated, errors: caught.map(describeError) };
  }

  it.each([
    { box: "no height (a full-width box that has collapsed)", width: 600, height: 0 },
    { box: "no width and no height", width: 0, height: 0 },
  ])("raises no unhandled error when it mounts in a box with $box", async ({ width, height }) => {
    const { errors } = await mountInBox(width, height);
    expect(errors).toEqual([]);
  });

  it("draws the graph, without error, in a box that has a size", async () => {
    const { chartCreated, errors } = await mountInBox(600, 320);
    expect(errors).toEqual([]);
    expect(chartCreated).toBe(true);
  });
});
