import type { components } from "./generated/schema";

export type ProblemDetail = components["schemas"]["ProblemDetail"];
export type FieldError = components["schemas"]["FieldError"];

/**
 * A non-2xx response, carrying the platform's one error shape (`00` §5.3).
 *
 * Thrown rather than returned so a caller cannot forget to check — and because every
 * failure here is exceptional in the ordinary sense: the alternative is `if (result.error)`
 * at 51 call sites, one of which will be missed.
 */
export class ProblemError extends Error {
  constructor(readonly problem: ProblemDetail) {
    super(problem.detail ?? problem.title);
    this.name = "ProblemError";
  }

  /**
   * The stable machine code. **Branch on this, never on `status`** — several codes share
   * a status, and `VALIDATION_HAS_FAILURES` and `WARN_NOT_ACKNOWLEDGED` are both 409 while
   * being two entirely different screens: one says fix the data, the other says an actuary
   * must sign it off.
   */
  get code(): string {
    return this.problem.code;
  }

  /**
   * The OpenTelemetry trace id. Show it wherever a user might report a problem: a support
   * conversation that starts with the trace id skips the reproduction step entirely.
   *
   * Optional, and correctly so. The backend sets it at all four construction sites, but
   * `current_trace_id()` returns null outside a traced operation and the platform declines
   * to invent one — a fabricated id would assert a correlation that does not exist. In
   * practice every problem from an HTTP request carries one; a problem built outside a
   * request, or synthesised here for a transport failure, may not.
   */
  get traceId(): string | undefined {
    return this.problem.trace_id ?? undefined;
  }

  get fieldErrors(): readonly FieldError[] {
    return this.problem.errors ?? [];
  }
}

/** Narrow an unknown rejection to a `ProblemError` for a specific code. */
export function isProblem(error: unknown, code?: string): error is ProblemError {
  return error instanceof ProblemError && (code === undefined || error.code === code);
}
