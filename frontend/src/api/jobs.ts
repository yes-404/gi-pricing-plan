import { request } from "./client";
import type { components } from "./generated/schema";

export type Job = components["schemas"]["Job"];
export type JobStatus = components["schemas"]["JobStatus"];

/** `queued` and `running` are the only states a job can leave. */
export const TERMINAL: readonly JobStatus[] = ["succeeded", "failed", "cancelled"];

export function getJob(jobId: string): Promise<Job> {
  return request<Job>(`/jobs/${encodeURIComponent(jobId)}`);
}

/**
 * Poll until the job reaches a terminal state, or `attempts` runs out.
 *
 * Polling rather than a socket because a job here is minutes at most and the platform has
 * no push channel yet (`07` §3.1). Returns the job in whatever state it is in when the
 * attempts run out — a caller must read `status`, not assume the wait succeeded, because
 * "still running after 60 s" and "failed" are different things to tell a user.
 */
export async function waitForJob(
  jobId: string,
  { attempts = 60, intervalMs = 1000 }: { attempts?: number; intervalMs?: number } = {},
): Promise<Job> {
  let job = await getJob(jobId);
  for (let n = 1; n < attempts && !TERMINAL.includes(job.status); n += 1) {
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
    job = await getJob(jobId);
  }
  return job;
}
