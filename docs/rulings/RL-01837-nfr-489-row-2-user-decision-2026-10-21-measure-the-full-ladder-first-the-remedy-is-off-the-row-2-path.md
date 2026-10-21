---
id: RL-1837
family: ruling
title: "NFR-489 / roadmap §12 row 2, the user's decision of 2026-10-21: measure the full ladder (25 → 200 rps, both arms) first; the remedy is built off the row-2 path; the budget is not changed now (16:03:00 supersedes the 16:00:01 plan)"
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-21   # filed 2026-10-21 under working id 8149; minted as RL-1837 2026-10-21
owner: decision-maker
tree: 57adb9e2a1efe01b07fa005a2ac1b738dfb45f93
phase: P2
work: WK-674
slice: SL-1455
supersedes: []
superseded_by: ~
corrected_by: []
relates: [WK-1178, FD-1836, RL-1685, RL-1755, LG-1760, PL-1454]
---

# RL-1837 — NFR-489 / roadmap §12 row 2, the user's decision of 2026-10-21: measure the full ladder first; the remedy is off the row-2 path; the budget is not changed now

Filed 2026-10-21 under working id 8149; minted as RL-1837 on 2026-10-21. **This is a record of a decision already made, not a new ruling** (`docs/process/document-ids.md` §1.6, RL: the maintainer may author one on scope; CLAUDE.md §13, "a decision already made is an RL-"). **The decision is the user's**, relayed by the maintainer (by delegation). The decision-maker seat writing this record decides nothing in it.

`work:` is `WK-1178` because `SL-1455` is a WK-1178 slice (`docs/roadmap.md`:2134 at 57adb9e2, "SL-1455 — WK-1178 fix slice"). `WK-674` is in `relates:` because FD 1836 names it as owner ("**HIGH; owner WK-674** (SL-1455's remedy; `docs/roadmap.md` §12 row 2 …)", FD-1836:17 at `origin/d29-records-2026-10-21` b49d3957). This record does not resolve that difference; it reports it.

## How this was decided — the sequence

Four entries in `~/gi-pricing-plan.local/channel/to-lead.md` are the source. The file is local, so each is quoted below, copied from it by `sed`, unedited.

1. **2026-10-21 16:00:01 BST — the first decision.** The user approved the maintainer's recommendation: a remedy slice time-boxed to about 2 days, no new cache (RL-1685), a re-measure on nfr-bench-1, a decision date of Mon 26 Oct 2026 with two outcomes (no-GBM p99 < 15 ms → row 2 met in full; otherwise the no-GBM limb carried forward in FD 1836 with a named owner, row 2 closing "with the GBM limb met"), and the budget not relaxed.
2. **2026-10-21 16:01:03 BST — the premise correction.** The 16:00:01 recommendation assumed "the GBM limb is met". It is met **only at 25 rps**; NFR-489 requires 200 rps per replica, and no 200 rps reading exists. Option (i) was ruled: the re-measure runs the full ladder 25 → 50 → 100 → 200 rps for both arms, first-OVER stops per arm; the remedy's acceptance adds handler time before and after. Option (ii), a GBM-only session now, was declined.
3. **2026-10-21 16:01:49 BST, item 3 — the remedy slice HELD.** perf-row2 estimates R1–R3 at ~3–6 ms, best ≈ 15.3–18.3 ms, so the fix is expected to miss 15 ms. With both premises of 16:00:01 changed, nothing more was cut until the user answered.
4. **2026-10-21 16:03:00 BST — the revised decision. It SUPERSEDES the 16:00:01 plan and is the operative decision.** The user chose "Measure first, fix off-path (Recommended)" after being told both changed premises.

**What is not operative:** the 16:00:01 entry's time-boxed remedy slice on the row-2 path, its Mon 26 Oct re-measure *of a remedy*, and its outcome "Row 2 closes with the GBM limb met". What carries over from 16:00:01 into 16:03:00 unchanged: no new cache (RL-1685), N = 4 and the 15:15:40 quiet threshold, pre-registration, and the budget not relaxed. What carries over from 16:01:03: the full ladder for both arms and first-OVER per arm (restated in 16:03:00 item 1).

## Verified first

- **The GBM limb at 25 rps only.** `~/gi-pricing-plan.local/scratch/nfr1-2026-10-21/logs/t4/inv01-r25.out` (local, 90 lines), under its heading `:55` "=== NFR-489 full path, with GBM (budget p99 < 50 ms) ===": `:66` "25 rps offered /   25.0 issued … p99   37.540 / 50 ms — PASS", `:67` "… implied ceiling   87.9 rps …"; `:70` "… p99   37.580 / 50 ms — PASS", `:71` "… implied ceiling   87.2 rps …". No other rate appears in that file's GBM section.
- **The budget.** `docs/specs/03-rating-engine.md`:1532 at 57adb9e2, NFR-489: "Real-time scoring p99 < 50 ms server-side at 200 rps per replica for a ~200-step motor structure with one `exact` GBM call (NFR-454). Without a GBM call, p99 < 15 ms."
- **The no-GBM limb.** FD-1836:39–41 at b49d3957: no-GBM handler "mean 18.378 ms, **p99 23.060 ms** (bench arm, :83–84); default-live arm handler p99 21.640 ms (:87–88). Both are over 15 ms server-side".
- **The remedy estimate.** `~/gi-pricing-plan.local/handover/perf-row2-options-2026-10-21.md`:49 (local): "**R1 + R2 + R3 (within the rulings): ≈ 3–6 ms** → best cell 21.27 → **≈ 15.3–18.3 ms**. Does **not** reliably reach < 15."
- **First-OVER, before this decision, stopped the session.** LG-1760:640 at `cb83e4e1` (`origin/nfr1-sl1455-task4-2026-10-21`): "**Stopped per the OVER rule** (`RL-1755` item 3; PL-1454 Task 4 Step 3) at the first OVER cell. **Not run: invocations 02 to 12** (11 of 12)". The 16:01:03 and 16:03:00 entries change that stop to **per arm**, for the new session only.
- **The quiet threshold.** LG-1760:605–612 at `cb83e4e1`, the addendum "2026-10-21 15:16 BST", on the entry "2026-10-21 15:15:40 BST" item 3: N = 4; "load1 < 1.0 before each invocation, wait up to 10 minutes, `pgrep -c pytest` = 0, `ps` top-5 limited to the harness, uvicorn, the stores and kernel threads", plus `load1` and `free -m` before and after each invocation.
- At `cb83e4e1`, LG-1760 has **no** full-ladder addendum yet (`git show cb83e4e1:<LG-1760> | grep -n -iE "ladder|first-OVER"` finds none). It is being written on `nfr1-sl1455-task4-2026-10-21` by exec-nfr1c; this record cites it by branch only.

## Ruled

Each entry's heading line is quoted without its leading `## `, so it does not become a heading of this record; nothing else is changed. The 16:01:49 item 3 names `handler/perf-row2-options-2026-10-21.md`; the file read here is `~/gi-pricing-plan.local/handover/perf-row2-options-2026-10-21.md` (no `handler/` file exists).

The entry "2026-10-21 16:00:01 BST" (`to-lead.md`:28438–28451 when read), verbatim — **superseded by the 16:03:00 entry below; kept as the record of what was first decided:**

> 2026-10-21 16:00:01 BST — Maintainer: USER DECISION, NFR-489 / §12 row 2: a time-boxed remedy, a fixed decision date, then a carry-forward if it misses. The budget is NOT relaxed.
> The user's words: "ok approve your recommendation for topic one, plz go ahead". The recommendation, as given to the user:
> 1. **Remedy slice, time-boxed to about 2 days of build.** It cuts per-request serial round trips: about 12 DB round trips (9 statements + pre-ping + BEGIN/ROLLBACK) plus 1 Redis, merged into fewer queries, with the pre-ping and the transaction wrapper dropped on the read path. **No new cache (RL-1685).** It must not delay the rest of row 2: the WF-699/WF-701 work continues in parallel.
> 2. **Re-measured on nfr-bench-1:** N = 4, the 15:15:40 quiet threshold, pre-registered, no-GBM and GBM arms. The user starts the VM; the maintainer asks with ≥ 2 h notice.
> 3. **Decision date: Mon 26 Oct 2026.**
>    - No-GBM p99 < 15 ms → row 2 met in full.
>    - Otherwise the no-GBM limb is **carried forward as an accepted finding with a named owner** (FD-1836, CLAUDE.md §14). Row 2 closes with the GBM limb met and the no-GBM gap recorded as measured. The 15 ms budget is reviewed in P3 through an OQ, on evidence.
> 4. **Not relaxing the budget now:** changing a target because it was missed, under deadline pressure, would lose the record of what was believed and why.
> **Lead actions:**
> - **(a) Verify the GBM limb (< 50 ms p99) from the existing readings, with file:line,** before anything else. If it is NOT met, STOP and report: the decision's premise changes.
> - **(b) Cut the remedy slice:** an SL row and its scope as one PR, under WK-674 (SL-1455's remedy line). Scope comes from perf-row2's options. The write set, the round-trip count before and after (a test asserting the statement and round-trip count, red-first), and the measurement protocol are named in it. The GO request comes to the maintainer.
>   - If perf-row2 sizes the remedy at well over 2 days, say so first. The recommendation was to go straight to the carry-forward in that case.
> - **(c) Record this decision as an RL in the next records batch** ("user decision, 2026-10-21"), citing this entry.
> - **(d) Tell the maintainer the earliest re-measure time,** so the user gets ≥ 2 h notice to start nfr-bench-1.

The premise correction, the entry "2026-10-21 16:01:03 BST" (`to-lead.md`:28453–28465 when read), verbatim:

> 2026-10-21 16:01:03 BST — Maintainer: the (a) STOP accepted; the premise is corrected; option (i) RULED. The user's 16:00:01 decision stands, with the re-measure widened
> - **Verified by the maintainer:**
>   - `scratch/nfr1-2026-10-21/logs/t4/inv01-r25.out:66-67,70-71`: GBM p99 37.540 / 37.580 ms PASS at **25 rps only**; "implied ceiling 87.9 / 87.2 rps".
>   - `03:1532` at 57adb9e2: "p99 < 50 ms server-side **at 200 rps per replica**".
>   - So the GBM limb is **met only at 25 rps**, and its 200 rps reading does not exist. My 15:58 recommendation's premise ("the GBM limb is met") was wrong. I took it from the escalation's framing without checking the rate.
> - **Ruled: (i).**
>   - The same remedy slice, cut now.
>   - Mon 26 Oct's re-measure runs the **full ladder 25 → 50 → 100 → 200 rps for BOTH arms**. The first-OVER rule stops per arm, not per session.
>   - The carry-forward on Mon 26 names **whichever limbs miss, at which rates**, with an owner (FD-1836, widened if the GBM limb misses).
>   - (ii) is declined. A GBM-only session now changes nothing we would build, and it costs a VM start.
> - **Remedy acceptance adds:** the per-request handler time (the CPU the "implied ceiling" is computed from), measured before and after on the same host and protocol.
> - **(b)–(d) are released:** cut the slice; record the decision as an RL, including this correction; give me the earliest re-measure time.
> - The maintainer tells the user the corrected premise. The fallback may now carry both limbs.

The entry "2026-10-21 16:01:49 BST", **item 3 only** (`to-lead.md`:28484 when read; items 1, 2 and 4 are other subjects), verbatim:

> **3. NFR-489 remedy slice: HELD, not cut.** perf-row2 (handler/perf-row2-options-2026-10-21.md) estimates R1–R3 save ~3–6 ms (best ≈ 15.3–18.3 ms), so the fix is expected to MISS 15 ms. With the GBM limb unmeasured at 200 rps, both premises of the 16:00:01 decision have changed. The maintainer puts a revised recommendation to the user. Nothing more is cut until the user answers.

The revised decision, the entry "2026-10-21 16:03:00 BST" (`to-lead.md`:28488–28498 when read), verbatim — **the operative decision:**

> 2026-10-21 16:03:00 BST — Maintainer: USER DECISION (revised), NFR-489 / §12 row 2: MEASURE FIRST, the fix is OFF the critical path. Supersedes the 16:00:01 plan.
> The user chose "Measure first, fix off-path (Recommended)" when asked, after being told both changed premises: the GBM limb is met only at 25 rps (implied ceiling ~88 rps), and perf-row2 estimates R1–R3 at ~3–6 ms, best ≈ 15.3–18.3 ms.
> 1. **ONE pre-registered full-ladder session on nfr-bench-1:** both arms, 25 → 50 → 100 → 200 rps, N = 4, the 15:15:40 quiet threshold; first-OVER stops per arm. About 1 h. The VM is stopped with its disk kept, so set-up is short. **Target start 18:05 BST today,** subject to the user starting the VM (≥ 2 h notice, given at this stamp).
> 2. **The row-2 dates are unchanged** (likely Fri 23, worst Mon 26 Oct). On Mon 26 Oct: met limbs are met; each missed limb is carried forward in FD-1836, with its rates, measured values and owner.
> 3. **The remedy (perf-row2 R1–R3; no cache, RL-1685) is built in spare capacity, OFF the row-2 path.** It merges only if gated green before the 4 Nov code freeze. If it merges, a re-measure updates FD-1836. It is cut as an SL row when seats allow, and its GO request comes to the maintainer.
> 4. **The budget is not changed now;** it is reviewed in P3 through an OQ, on the 200 rps readings.
> **Lead actions:**
> - (a) Pre-register the session protocol as an LG-1760 addendum and push it by 17:50 BST.
> - (b) Seat exec-nfr1c for 18:05 BST.
> - (c) Record both the 16:00:01 decision and this revision as one RL in the next records batch.
> - (d) Cut the remedy SL row when capacity allows.

## Who decided, and when

- **The user** decided twice: at 16:00:01 BST ("ok approve your recommendation for topic one, plz go ahead") and at 16:03:00 BST ("Measure first, fix off-path (Recommended)"), both on 2026-10-21, both relayed by the maintainer (by delegation).
- **The maintainer (by delegation)** corrected the premise and ruled option (i) at 16:01:03, and held the remedy slice at 16:01:49.
- **The budget is not relaxed, and why** (16:00:01 item 4, carried into 16:03:00 item 4): changing a target because it was missed, under deadline pressure, would lose the record of what was believed and why. It is reviewed in P3 through an OQ, on the 200 rps readings.

## What it obliges

What the operative decision (16:03:00) obliges:

1. **One pre-registered full-ladder session on nfr-bench-1** (16:03:00 item 1): both arms (no-GBM and GBM), 25 → 50 → 100 → 200 rps, N = 4, the 15:15:40 quiet threshold, first-OVER stops **per arm**. It is pre-registered as an **LG-1760 addendum on `nfr1-sl1455-task4-2026-10-21`** (being written by exec-nfr1c), pushed by 17:50 BST before the first timed command (lead action (a)); target start 18:05 BST, subject to the user starting the VM.
2. **Row-2 dates unchanged** (16:03:00 item 2: likely Fri 23, worst Mon 26 Oct). **On Mon 26 Oct:** met limbs are met; **each missed limb is carried forward in FD 1836, naming the limb, the rates it missed at, the measured values and the owner** — FD 1836 is widened if the GBM limb misses (16:01:03).
3. **The remedy (perf-row2 R1–R3; no cache, RL-1685) is built OFF the row-2 path** (16:03:00 item 3), in spare capacity. It is cut later as an SL row (planned as **PL 8147 / SL 8148**, working ids), its GO request goes to the maintainer, and it merges **only if gated green before the 4 Nov code freeze**. Its acceptance carries the 16:01:03 addition: the per-request handler time, measured before and after on the same host and protocol. If it merges, a re-measure updates FD 1836.
4. **The budget is not changed now** (16:03:00 item 4). **An OQ in P3** reviews it, on the 200 rps readings.
5. Nothing in this record edits `docs/specs/03-rating-engine.md`, `PL-1454`, `LG-1760` or FD 1836.

## Acceptance — the violation that must become detectable

This record answers how row 2's NFR-489 limb is decided; no check can fail on a broken input. The violation to catch by reading: *Violation: the Mon 26 Oct row-2 close reports the GBM limb met from the 25 rps reading alone; or a session stops both arms at one arm's first OVER; or a carry-forward in FD 1836 omits a missed limb, its rates, its values or its owner; or the remedy merges after the 4 Nov code freeze or on the row-2 path; or NFR-489's 15 ms / 50 ms is changed before the P3 OQ.* The reviewer reads LG-1760's full-ladder addendum and readings, and FD 1836, against the quoted entries.
