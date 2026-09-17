import { request } from "./client";
import type { components } from "./generated/schema";

export type Backtest = components["schemas"]["Backtest"];
export type BacktestSummary = components["schemas"]["BacktestSummary"];

/**
 * One stored backtest, by its own id (FR-94, `02` §5.1).
 *
 * Not nested under the model: a model has many backtests — one per period it has been
 * measured against — so unlike `Diagnostics` there is no "the" backtest for a model to fetch.
 * A caller who has just run one reaches it through the Job's `backtest:{id}` result.
 */
export function getBacktest(backtestId: string): Promise<Backtest> {
  return request<Backtest>(`/models/backtests/${encodeURIComponent(backtestId)}`);
}

/**
 * The period the backtested version covers, or null when it declares none.
 *
 * Both fields are **optional and nullable**, so absence arrives as `null` from the wire and
 * as `undefined` from an omitted key, and neither may render as an empty date. A one-sided
 * window is a real state: `backtests.py`'s ordering validator only fires when both ends are
 * present.
 *
 * The caption is deliberately not built from this (FR-187) — a period in a column
 * heading would assert a relationship the artifact does not carry.
 */
export function periodLabel(summary: BacktestSummary): string | null {
  const from = summary.period_from ?? null;
  const to = summary.period_to ?? null;
  if (from !== null && to !== null) return `${from} to ${to}`;
  if (from !== null) return `from ${from}`;
  if (to !== null) return `to ${to}`;
  return null;
}
