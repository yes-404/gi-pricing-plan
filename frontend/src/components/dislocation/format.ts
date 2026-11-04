import { formatAmount } from "@/components/sandbox/ladder";

/** A derived percentage (03 §4.6: null where its denominator is zero) for display. */
export function formatPct(value: number | null | undefined): string {
  return value === null || value === undefined ? "—" : `${value.toFixed(2)}%`;
}

/** A share in [0, 1] as a percentage. */
export function formatShare(value: number | null | undefined): string {
  return value === null || value === undefined ? "—" : `${(value * 100).toFixed(1)}%`;
}

/** Minor units as major units with two places and no currency symbol (OQ-551). */
export function formatMinor(minor: number | null | undefined): string {
  return minor === null || minor === undefined ? "—" : formatAmount(minor);
}
