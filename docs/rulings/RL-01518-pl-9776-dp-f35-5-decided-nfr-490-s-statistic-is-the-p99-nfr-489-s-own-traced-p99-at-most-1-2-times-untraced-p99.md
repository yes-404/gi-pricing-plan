---
id: RL-1518
family: ruling
title: PL-1520 DP-F35-5 decided — NFR-490's statistic is the p99, NFR-489's own; traced p99 at most 1.2 times untraced p99
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-08            # original date 2026-10-01, set at the draft; minted 2026-10-08
owner: decision-maker
tree: 1dd5e264195677b4a13268b80ac8673c2c027135
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [NFR-489, NFR-490, RL-862, RL-863, CR-1247, SL-1259, WK-1178, FD-1437, RL-1519, PL-1520]
---

# RL-1518 — PL-1520 DP-F35-5 decided: NFR-490's statistic is the p99

**A spec interpretation, so it needs the maintainer's acceptance** (see "Acceptance" below).
It is kept separate from RL-1519, which rules DP-F35-1, -2 and -3, because
it interprets a requirement rather than deciding a design. PL-1520 (draft PR
#1051, read at head `9a2ebc56`) activation need 2 checks each DP on its own. This record
(working id 9770), RL-1519 (9771) and PL-1520 (9776) were minted together on 2026-10-08
(batch B4).

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-f35`
(`CLAUDE_EFFORT=high`, printed by this session). The order came in the same brief as
RL-1519. The lead relayed the maintainer's lean: "p99 IF NFR-489 uses p99 (03:1190 reads
'p99 < 50 ms'); verify". All facts were read at `origin/main`
`1dd5e264195677b4a13268b80ac8673c2c027135`, 2026-10-01, 10:01–10:40 BST.

## Verified first

| Fact | Where, at `1dd5e264` |
|---|---|
| NFR-490: "Tracing adds ≤ 20 % to scoring latency and never changes the result (R3)." No statistic | `docs/specs/03-rating-engine.md:1194` |
| NFR-489 states its budget at p99: "Real-time scoring p99 < 50 ms server-side at 200 rps per replica for a ~200-step motor structure with one `exact` GBM call (NFR-454). Without a GBM call, p99 < 15 ms." The plan's `:1190` was the line at `19155b50`; it is `:1193` now | `03:1193` |
| `RL-862` records the gap: "NFR-490 names no statistic (filed separately by the lead)" | `docs/rulings/RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md:249` |
| `RL-862` §6: NFR-490 "is violated whenever a trace is produced at all, wherever that happens" | same file, `:137-141` |
| The instrument prints NFR-490 at p99 against `BUDGET_TRACE_OVERHEAD = 0.20`: "NFR-490 — trace overhead at p99: …" | `scripts/bench-rating.py:77`, `:970-973` |
| F35's register row records +497 % to +723 % over 5 of 5 runs on a 200-step motor structure, measured with that instrument | `docs/findings/register.md:77` |

**The maintainer's condition holds:** NFR-489 states its budget at p99.

## Options, weighed

- **(a) p99.** It is the statistic of the latency budget on the same path (NFR-489). The
  two budgets are then read with one statistic: a traced call that meets NFR-490 against an
  untraced p99 that meets NFR-489 is bounded at 1.2 × 50 ms at p99. It is what the harness
  prints and, per PL-1520, what F35 and `#1045`'s bench line read, so no earlier figure is
  re-read. The harness's own docstring (`bench-rating.py:488-492`) warns that the p99 alone
  "cannot distinguish a cost that multiplies the whole distribution from one that only
  fattens the tail". The ratio ladder answers that question as a diagnostic, and the budget
  stays one statistic.
- **(b) the mean.** It hides a tail cost, which is where a payload-copy overhead shows
  first. No other `03` latency budget is stated as a mean.
- **(c) every quantile.** The harness's ratio ladder (`bench-rating.py:990`) is a
  diagnostic of where the cost sits. As a budget it multiplies the verdicts and lets the
  noisiest quantile decide.

## Ruled

**(a) p99.** NFR-490's budget holds when the p99 of scoring latency with a trace requested
is at most 1.20 × the p99 without one. Both are measured:
- for the same algorithm, the same Quote Contexts and the same host;
- in the same window;
- on NFR-489's reference structure: about 200 steps with one `exact` GBM call.

It applies wherever a trace is produced, on the request path or off it (`RL-862` §6). A
mean, a median or another quantile is diagnostic and does not satisfy it.

**What this does not decide.** It sets no verdict on NFR-490: that is `SL-1259`'s, on the
dedicated host (the maintainer's 2026-10-01 09:00:44 BST entry, as PL-1520 quotes it). It
sets no run count or margin rule either: PL-1520's "How NFR-490 is measured" already states
those, and this ruling only fixes the statistic they read.

## The spec text, verbatim

**Placeholders**, and only these: `{DATE}` is the date the text is applied (`YYYY-MM-DD`).
`{RL-1518}` is this record's minted id, written `RL-<n>`.

**NFR-490**, replacing the whole row at `03:1194` (`03:1331` at `ef5dc6e7`). It is applied in this record's mint PR,
which PL-1520 activation need 2 checks for (`grep -cE '(Clarified|Amended) 2026-1[0-2]'` on
NFR-490's row):

```text
| **NFR-490** | Tracing adds ≤ 20 % to scoring latency and never changes the result (R3). *(Clarified {DATE}, {RL-1518}: the statistic is the p99, NFR-489's own. The budget holds when the p99 of scoring latency with a trace requested is at most 1.20 × the p99 without one, for the same algorithm, Quote Contexts and host, measured in the same window on NFR-489's reference structure (about 200 steps with one `exact` GBM call). It applies wherever a trace is produced, on the request path or off it (`RL-862` §6). A mean, a median or another quantile is diagnostic and does not satisfy it. `scripts/bench-rating.py` prints it as "NFR-490 — trace overhead at p99", against `BUDGET_TRACE_OVERHEAD`.)* |
```

**The executor applies each text above byte-for-byte; authorship stays with the
decision-maker (document-ids §1.6 FR row; CLAUDE.md §2 one-commit rule; the RL-1296
precedent). Any executor wording is a stop.**

## What it obliges

- **This record's mint PR** applies the NFR-490 text, but only after the maintainer's
  acceptance line below is dated. The ruling is then set `active`.
- **PL-1520 Tasks 1 and 6** read the margin statement of "How NFR-490 is measured" at p99, as
  written. No method difference arises.
- **`SL-1259`'s NFR-490 verdict** reads the same statistic, on the dedicated host.

## Acceptance — the violation that must become detectable

1. **The text is on the row.** This command prints `1` on `main` after the mint, and `0` at
   `1dd5e264`. It is PL-1520 activation need 2's third command:

   ```bash
   git show "$M":docs/specs/03-rating-engine.md | grep -E '^\| \*\*NFR-490\*\*' | grep -cE '(Clarified|Amended) 2026-1[0-2]'
   ```

2. **A verdict on another statistic is not evidence.** A ledger or closure record that books
   NFR-490 as passing on a mean, a median or a ratio ladder alone, without the p99 line
   `bench-rating.py` prints, is refused at audit. The auditor reads the p99 line by name.

## Maintainer acceptance

This ruling interprets a requirement, so it binds only once the maintainer accepts it. The
maintainer's lean was (a), conditional on NFR-489's statistic, and that condition is
verified above. Until the maintainer's dated line below is filled in, PL-1520's Tasks 1
and 6 read p99 provisionally, and the text above is not applied.

**Maintainer acceptance:** Accepted by the maintainer (by delegation), 2026-10-01 10:30:00 BST (to-lead.md entry headed '2026-10-01 10:30:00 BST — ACCEPTANCE: RL 9770 (NFR-490's statistic = p99) as the spec interpretation; FD 9759 limb (2) discharged at the compile site alone; #1060 audit noted'): NFR-490's statistic is the p99, as ruled; the row text applies at mint.

*(Recorded by the decision-maker on the lead's relay. This session did not read the channel
file. The status stays `draft`; the mint PR applies the NFR-490 row and sets this record
`active`.)*

## Amendment, 2026-10-05: citations re-read at main `ef5dc6e7`, before mint

Citation and currency update only. Nothing ruled above changes (decision-maker `dm-amend-2`,
on the lead's brief of 2026-10-05 10:50 BST, which adopted the batch-2 triage).

- **The NFR-490 row moved `03:1194` → `:1331`** and is byte-identical to `1dd5e264`.
  NFR-489, which this record reads, moved `03:1193` → `:1330` and is unchanged, so the
  premise "NFR-489 states its budget at p99" holds. The `03:1190` inside the lead's relay
  (*How this was ruled*) is a quotation and stays as quoted.
- **Moved code cites:** `bench-rating.py:970-973` → `:978-981`, `:990` → `:998`.
  `bench-rating.py:77` and `:488-492` are unchanged.
- `tree:` stays `1dd5e264`. `status:` stays `draft`, as the acceptance note above records:
  the mint PR applies the row and sets the record `active` (done in batch B4, 2026-10-08;
  PL-1520 and RL-1519 are minted in the same batch).
