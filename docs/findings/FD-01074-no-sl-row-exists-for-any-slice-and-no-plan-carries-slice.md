---
id: FD-1074
family: finding
title: No SL- row exists for any slice, and no PL- carries a slice: field
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-18
owner: lead
tree: d63f765085fe6eb1c594177c5779ecfc3caf7ae8
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
---

# FD-1074 — No `SL-` row exists for any slice, and no `PL-` carries a `slice:` field

## Finding

`docs/process/document-ids.md` §1.5's header template lists `slice: SL-NNNNN` as a field that
applies to a `kind: leaf` plan, and §1.9 documents `SL-<n>` as the GitHub-native mirror of a
slice (branch `sl-<n>-<slug>`, PR title `SL-<n>: <title>`). At `d63f765085fe6eb1c594177c5779ecfc3caf7ae8`,
**no `SL-` row has ever been minted anywhere in the tree, and no `PL-` file has ever carried a
`slice:` field.** Every W37 slice (W37-1 … W37-11) is instead recorded as a named clause
inside `docs/roadmap.md`'s `WK-697` row, not as its own `SL-` row.

This is not a W37-6 migration defect and does not postdate it: `SL-` as a family and `slice:`
as a field are both introduced by `RFC-937` itself (the same RFC the W37-6 migration
implements), and the population of `SL-` rows was never populated by that migration or by any
Work before it — the gap predates every governed record this repository's id system currently
tracks. `docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md`, the only leaf plan on
`main` before the current Stage-3 batch, already omits `slice:`, and three Stage-3 leaf-plan
drafts independently reached the same disposition while under review (PR #789's DP-7-5-adjacent
note, PR #790's DP-8.4, PR #791 R5) — each reasoning from the same evidence this record cites,
and the lead ruled it explicitly during the same review pass: omit the field, cite the slice in
prose, and non-block on it.

## Evidence

```
$ git show origin/main:docs/roadmap.md | grep -cE '\bSL-[0-9]'
0
$ for f in docs/plans/*.md; do grep -c '^slice:' "$f"; done | awk '{s+=$1} END{print s}'
0
```

Both measured at `d63f765085fe6eb1c594177c5779ecfc3caf7ae8`, the tree this record was filed
against. `scripts/doc-id.py:7374`'s own header-scan guard, `if header.slice_ is not None:`,
confirms the field is optional by construction — a plan that omits `slice:` never enters the
`_resolves_to_row` check at all, so the omission is clean rather than a latent failure waiting
for the first `SL-` row to expose it.

## Disposition

**Deferred with an owner — W37-10**, the slice that owns `docs/roadmap.md` (`PL-939:815`).
Backfilling the `SL-` rows for WK-697's eleven slices — the map plan's own `PL-939:692`
already describes this as something the map plan's parent *will* mint, not something any single
leaf plan should do piecemeal — is a `docs/roadmap.md` edit, and doing it for all eleven at once
rather than one slice at a time is the right unit of work per the same reasoning the Stage-3
drafts already gave independently. **Verified at the Work close by W37-11**, per `CLAUDE.md`
§13's evidence discipline: W37-11 closes `WK-697` and is the natural point to confirm either
that the `SL-` rows now exist and every `PL-`/`LG-` in scope carries a resolving `slice:`, or
that the omission is carried forward again with a fresh, dated reason.
