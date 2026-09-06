import { ProblemError, type ProblemDetail } from "./problem";

/**
 * The one place that talks to the platform.
 *
 * Deliberately thin. Everything it knows is a platform convention that would otherwise be
 * re-learned at every call site: the single error shape, the trace header, and that a
 * long operation answers `202` with a Job rather than a result.
 *
 * It knows **no** data shapes. Those come from `./generated/schema`, which is generated
 * from `model-schema` and never hand-written (`CLAUDE.md` §2) — a shape defined twice will
 * diverge, and here a diverged shape is a mispricing.
 */

const BASE = "/api/v1";

let currentAccessToken: string | null = null;

/** The bearer token subsequent requests carry (07 FR-393). Set by the auth session;
 *  null sends no Authorization header and lets the platform refuse (07 §3.7). */
export function setAccessToken(token: string | null): void {
  currentAccessToken = token;
}

export function clearAccessToken(): void {
  currentAccessToken = null;
}

let currentWorkspaceId: string | null = null;

/** The workspace subsequent requests act in (07 FR-397). Set by the workspace store;
 *  null sends no header and lets the platform refuse or default (07 FR-396). */
export function setWorkspaceId(id: string | null): void {
  currentWorkspaceId = id;
}

export interface RequestOptions {
  readonly method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  readonly body?: unknown;
  readonly query?: Record<string, string | number | undefined>;
  /**
   * `00` §5.4 — sent on every POST that creates a Job or artifact. A double-clicked
   * "Validate" must not start two runs, and neither must the retry an HTTP client performs
   * on a dropped connection.
   */
  readonly idempotencyKey?: string;
  readonly signal?: AbortSignal;
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const url = new URL(`${BASE}${path}`, window.location.origin);
  for (const [key, value] of Object.entries(options.query ?? {})) {
    if (value !== undefined) url.searchParams.set(key, String(value));
  }

  const headers: Record<string, string> = { Accept: "application/json" };
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  if (options.idempotencyKey) headers["Idempotency-Key"] = options.idempotencyKey;
  if (currentWorkspaceId) headers["Workspace-Id"] = currentWorkspaceId;
  if (currentAccessToken) headers["Authorization"] = `Bearer ${currentAccessToken}`;

  // Spread rather than assign `undefined`: `exactOptionalPropertyTypes` distinguishes
  // "absent" from "present and undefined", and `RequestInit` accepts the first only.
  const response = await fetch(url, {
    method: options.method ?? "GET",
    headers,
    ...(options.body === undefined ? {} : { body: JSON.stringify(options.body) }),
    ...(options.signal ? { signal: options.signal } : {}),
  });

  if (!response.ok) throw new ProblemError(await readProblem(response));
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

/**
 * Read the error body as a `ProblemDetail`, or synthesise one.
 *
 * The platform returns this shape for every non-2xx and a test enforces it — but a proxy
 * timing out in front of the API does not, and a client that assumed the shape would throw
 * a `TypeError` about `undefined.code` and hide the actual failure.
 */
async function readProblem(response: Response): Promise<ProblemDetail> {
  const traceId = response.headers.get("traceresponse");
  try {
    const body = (await response.json()) as Partial<ProblemDetail>;
    if (typeof body?.code === "string") return body as ProblemDetail;
  } catch {
    // Falls through to the synthesised problem below.
  }
  return {
    type: "about:blank",
    title: response.statusText || "Request failed",
    status: response.status,
    // Not a platform code — the platform did not produce this response. Deliberately
    // distinguishable, so a client never mistakes a proxy timeout for a domain refusal.
    code: "TRANSPORT_ERROR",
    detail: `The response to ${response.url} was not a problem document.`,
    errors: [],
    ...(traceId ? { trace_id: traceId } : {}),
  };
}
