---
id: RL-1830
family: ruling
title: SL-1575 acceptance 5 runs as option (a), a 19,985-row slice of the pinned book, with the corrected argv `acc5 cost --policies 19985 --runs 1`
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-19   # filed 2026-10-19 under working id 8133; minted 2026-10-19 as RL-1830
owner: decision-maker
tree: 1aab7a21fc5732ac6c0ea0c47d02ac4980638220
phase: P2
work: WK-1178
slice: SL-1575
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1574, LG-1826, WK-1178]
---

# RL-1830 — SL-1575 acceptance 5 runs as option (a), a 19,985-row slice of the pinned book, with the corrected argv `acc5 cost --policies 19985 --runs 1`

Filed 2026-10-19 under working id 8133 (a working id until a later seat mints it). The ruling is the maintainer's (by delegation). Its sources are the entries "2026-10-19 07:06:05 BST" and its CORRECTION "2026-10-19 07:06:58 BST" in `~/gi-pricing-plan.local/channel/to-lead.md`.

## How this was ruled

Two entries in `~/gi-pricing-plan.local/channel/to-lead.md` are the source, and both are named here: "2026-10-19 07:06:05 BST" and its CORRECTION "2026-10-19 07:06:58 BST". The file is local, so both are quoted below, copied from it by `sed`. **The correction changes the argv:** the 07:06:05 entry gave `inv-rss.sh acc5 --policies 19985 ...`, which "lacked the subcommand"; the 07:06:58 entry rules `inv-rss.sh acc5 cost --policies 19985 --runs 1` (ks default "3,4,5,6"). Where they differ, the 07:06:58 entry governs. The 07:06:05 entry's other content (the option, the reason, the disclosure, the conditions) is not corrected by it.

## Verified first, at 1aab7a21fc5732ac6c0ea0c47d02ac4980638220

- `docs/plans/PL-01574-*` line 555 reads "The target is a plan acceptance target, not an NFR: peak RSS ≤ 15.5 GiB and ≤ 60 min per" and continues "dislocation run at the R6 size" (the entry quotes it as one string).
- The entry "2026-10-19 08:37:07 BST" records acceptance 5's result (PASS), read by the maintainer; it is the outcome and is not part of this ruling.

## Ruled

The entry "2026-10-19 07:06:05 BST", verbatim (the **(1) SL-1770** part is not this ruling's subject; it is quoted because it is one entry):

> **(1) SL-1770:**
> - the lead's adoption of CLEAN (LG 8126 @dc0ff6ec) is accepted;
> - DP-7 holds (a4d1f08c3b97 → 5c8e3b71d094; main has no migration since aea6f160);
> - F1/F2 are closing acts; F4 → SL-1771 (PL-1769:69).
> The mint follows SL-1259's push. At ACK I read the written audit.
>
> **(2) SL-1575 acceptance 5 — GO on option (a)** `cost --policies 19985`.
> - **Why:** acceptance 5 measures per-policy attribution cost at R6's SIZE (R6 (A1): "FR-263 sets no size"). A 19,985-row slice of the same pinned book (ARFF sha a45363e0…) carries that quantity, while (b) would change the instrument.
> - **Disclosed in LG 8125:** "first 19,985 rows by quote_id, not the seed's sampled set (seed.py build_portfolio_csv)". Recorded as an interpretation; it rides D26 with the other RLs.
> - **Diff (scratch/sl1575-acc5/inv-rss.diff), read by me:** only W/O re-pointed, mkdir, the END line and exit rc; the method is unchanged. **Accepted.**
> - **ALONE, made real at launch** (the script takes no lock): `setsid nohup flock -w 60 /tmp/slots/gate-1 flock -w 60 /tmp/slots/gate-1b bash …/inv-rss.sh acc5 --policies 19985 >/dev/null 2>&1 </dev/null &`.
>   - Precheck: gate-2 is free, `free -m` ≥ 8192, load1 ≤ 2.0. Quote PID, PGID, PPID=1 and SID.
>   - **No other run beside it.** The SL-1259/1770 edit or mint seats may continue: no tests, no checks.
> - **Report:** END first, then peak RSS + wall time + per-policy cost, against acceptance 5's own threshold line (quote it from PL-1574).

The correction, the entry "2026-10-19 07:06:58 BST" (a single line in the file), verbatim:

> 2026-10-19 07:06:58 BST — Maintainer: CORRECTION to 07:06:05 (my argv lacked the subcommand; the lead was right not to guess). SL-1575 acc 5 = option (ii): `inv-rss.sh acc5 cost --policies 19985 --runs 1` (ks default "3,4,5,6"), launched as ruled (setsid nohup flock gate-1 + gate-1b; gate-2 free, free -m ≥ 8192, load1 ≤ 2.0). Report against PL-1574:555 "peak RSS ≤ 15.5 GiB and ≤ 60 min per dislocation run at the R6 size": peak RSS from $n.rss, and EACH dislocation run's wall time as cmd_cost prints it (one per k). If cmd_cost prints only a total, report that and say so; I then rule on the per-run reading

## What it obliges

- `LG-1826` carries the disclosure the 07:06:05 entry names: "first 19,985 rows by quote_id, not the seed's sampled set (seed.py build_portfolio_csv)".
- The report is made against PL-1574:555 per the correction: peak RSS and each dislocation run's wall time; if only a total is printed, say so and the maintainer rules on the per-run reading.
- `PL-1574` is not edited.

## Acceptance — the violation that must become detectable

This ruling answers how an acceptance measurement is run; no check can fail on a broken input. The violation to catch by reading: *Violation: acceptance 5 is reported from a run whose argv lacks the `cost` subcommand, or from a different row count than 19,985, or without the LG disclosure.* The reviewer reads `LG-1826` against the quoted entries.
