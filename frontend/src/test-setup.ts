import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";

/**
 * Register row F39: the suite opened a TCP connection to port 3000, which is the test
 * environment's default origin, because a test reached the network through `fetch` without
 * stubbing it. Harmless while the connection is refused. It turns into a silent flake where
 * something answers on that port. A test that needs `fetch` stubs it
 * (`vi.stubGlobal("fetch", …)`); any other call fails the test that made it, by name.
 */
const unstubbedFetches: string[] = [];

globalThis.fetch = ((input: RequestInfo | URL) => {
  const url = input instanceof Request ? input.url : String(input);
  unstubbedFetches.push(url);
  return Promise.reject(new Error(`unstubbed fetch in a test: ${url}`));
}) as typeof fetch;

afterEach(() => {
  if (unstubbedFetches.length > 0) {
    const urls = unstubbedFetches.splice(0).join(", ");
    throw new Error(`F39: this test called fetch without stubbing it: ${urls}`);
  }
});
