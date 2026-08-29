# W11 process-conformance audit — is the team following `delivery-process.md`?

**Maintainer-requested, 2026-08-29.** Scope: today's W11 conduct against
[`delivery-process.md`](../process/delivery-process.md) §§5, 6, 7, 8 and 15 — per-layer
flow, the Slice TDD cycle, escalation-guard instrumentation, parallelism, and
message/correction discipline. Directed to audit the lead hardest, since that is where
conformance is least checked, and produced independently of the lead's own list (not
seen before this was written).

**Evidence**: merged PRs #395-402, all twelve `docs/plans/2026-08-29-*.md` files, `git log
origin/main` (read at `eda085f9`, current tip at write time), and
`/home/puzhenhao1989/w11-handover-2026-08-29/lead-rulings.md` (R1-R8, the eight rulings
named in the request — M1 is the maintainer's, correctly kept separate in that file and
excluded here). Every timestamp below is UTC; git's default rendering is `+01:00` and was
converted, not read raw (`git-hygiene`'s own documented trap).

**Verdict, ahead of the detail: substantively followed, with one real defect (not two
false-and-fixed occurrences of the same defect, §8), one verified factual error in a lead
ruling (§15/R2), one instrumentation obligation not assembled (§7), and one structural
gap in what the tooling can prove about §5's merge-authority rule at all.** Propose:
accept with the findings below carried to the register or the §14 review as appropriate —
none blocks W11, none is a defect in what was built.

## §5 — Per-layer flow

**Text**: lead holds sole merge authority; auditor proposes fix/accept/defer, lead
adopts/amends/rejects; decision-maker rules decision points and spec-vs-code conflicts
only, never audit verdicts.

**Followed, on the evidence available — with a limitation stated rather than smoothed
over.** PR #400 (Task 1.2) shows the intended shape precisely: the auditor (this role)
proposed a split verdict (one flagged decision executor-appropriate, one
decision-maker-shaped); the lead held the PR rather than merging a green gate (R7,
18:03Z) instead of ruling it personally; the decision-maker ruled (Ruling 22, PR #401,
merged 18:13:49Z); the fix landed (`5b05a628`, committed 18:44:48Z) and R8 records the
lead pre-reviewing it at 18:36Z, before the gate landed. Every role stayed in its own
lane on this evidence.

**What cannot be verified**: `gh pr view --json mergedBy` returns `yes-404` for all eight
PRs — one shared authenticated identity across every role in this environment. There is
no tooling signal distinguishing "the lead merged this" from "a role self-merged under
the shared account," so §5's "sole merge authority" and executor.md's "never merges a
pull request" are enforced by instruction, not provably by anything an auditor can check
after the fact. This is the same shape as this project's own standing finding that
enforcement by construction needs a closed write-set, not an unfound second writer — here
there is no write-set to close at all with the current tooling. Not asserted as a
violation; asserted as an unverifiable control, which for a rule this load-bearing is
itself worth recording.

## §6 — Slice TDD cycle

Task 1.2 (the only executor slice that ran today) shows the cycle in the plan's own
checkbox structure and the PR's account of following it: Step 1 wrote a failing resolver
test, Step 2 ran and confirmed the predicted failure by its exact error code and detail
string (not just "it failed"), Step 3 implemented the three branches. The PR's
"Verification" section goes beyond bare TDD into mutation testing on all three
load-bearing claims (revert, confirm the documented failure, restore) — stronger than
what §6 requires, not merely compliant with it. Independently re-run for the Ruling 22
delta specifically (not just read): both affected test files pass in full against
`5b05a628` (8/8 each, both counts reconciling exactly against the diff), `ruff` clean,
full-project `mypy` clean at 147 source files.

§6 step 4's own caveat — "not yet built as a blocking hook... an implementation gap, not
a document conflict" — is accurate as stated, not a discovered gap of this audit's own.

## §7 — Escalation guards

Task 1.2 is explicitly the pilot this section's instrumentation was written to start
logging from. Its actual guarded-loop count: **one** iteration (audit finds a gap → held
rather than merged → decision-maker rules → executor fixes → auditor re-verifies), well
inside the Slice-layer cap of ≤ 2. Two things worth separating:

- **The retry cap itself was respected.** No slice needed a second loop.
- **The specific instrumentation obligation — "log every... per-slice re-audit count and
  gate re-run from the first slice run under this process" — was not assembled anywhere
  as a single artifact.** The facts exist, scattered: this auditor's two PR #400 passes,
  R7/R8 in `lead-rulings.md`, the delta commit. A search for "re-audit count" / "gate
  re-run" against `origin/main` finds only the rule's own definition and discussion of
  adopting it, never a filed count for Task 1.2 itself. §7 says the numbers get revisited
  "once a workstream's worth of data exists" — that revisiting has nothing to read yet.
  This is the same shape this project already has a name for: a documented mechanism
  with a reader and no writer (pilot finding P6, F31). Recommend: this record itself can
  serve as that first data point (**pilot slice, Task 1.2: 1 audit-fix loop, 2 auditor
  passes, gate re-run confirmed independently**), but nothing yet commits to writing the
  next one.

## §8 — Parallelism

**No violation found at the layer this rule actually governs.** §11's own "process-slice
vs. plan-heading" distinction (pilot finding P4) is the right lens: today's ruling PRs for
Slices 2-4 (#396, #397, #398, #402 — DP1/DP2, D4/F1/M4, three more rulings) all merged
*while* Task 1.2 (the one process-slice actually executing today) was still open. That is
not two slices running at once: ruling-filing is Work-layer decision-point resolution
(§5 step 3, and decision-maker.md's own charter to "pre-resolve every decision point
before its slice starts"), not Slice-layer execution (write-test/implement/gate). §8
governs the latter. Confirmed none of the four ruling PRs touch code (`git diff --stat`
on each: `docs/plans/`, `docs/specs/`, `docs/skills-map.md` only) — decision-maker.md's
"no write access to any code worktree" held throughout.

**A real violation did occur earlier today, twice, before the fix that worked landed —
this is squarely in scope and should not be waved through because it predates this
session's own tasks.** Reconstructed from `git log origin/main`, `TZ=UTC`:

1. **First occurrence** (`21fe67b`, 15:48:59Z): executor and auditor each independently
   ran the full suite on PR #371, neither aware of the other — load average 11.17 on a
   box already carrying twelve agent processes. Filed as pilot finding P14, correctly
   scoped: §8 governs parallelism between slices, not between roles verifying one
   artifact — a real gap the rule as originally written did not cover.
2. **Recurrence ten minutes later** (`9c12d80`, 15:58:50Z), proving the first fix was the
   wrong shape: "a role checks whether one is already in flight" is unactionable when the
   only record of what is in flight is a pairwise message to someone else — the executor
   dispatched its own CI watcher while the lead's was already running, then the auditor
   dispatched a third, unaware of the first two.
3. **The fix that actually held** (`4ec7fd1`, 16:11:46Z) landed in §8's own text:
   announce an expensive verification when starting it, prefer CI over a local re-run for
   a pushed branch, and — the operative correction — coordination state must be visible,
   not relayed pairwise.
4. **No third occurrence found** in the 18:00-19:00Z window today (the only three commits
   in that window are the #400/#401/#402 merges; none shows a fresh full-suite dispatch).
   Stated as absence of evidence in the repository, not proof nothing ran unfiled — this
   audit cannot see a local process that left no artifact.

## §15 — Correction and message discipline

The section's own text already names its worst example against itself (miscounting "three"
while listing four) and narrates several real 2026-08-29 failures. One further instance,
not already in that list, found by checking every "gate clean" claim today against its
CI corpus: `f5fbcc1` (15:51:07Z) is a **second**, separate false "clean" claim on PR #371
— the auditor's own closure record had claimed a "full gate ... all clean" that had
actually run ruff/mypy/lint-imports/audit-docs plus one test file, never `pytest -q`; the
real CI run showed one genuine failure (a contract-drift defect). **The correction of it
is itself a compliant example**: its first sentence names exactly which claim was wrong,
unhedged. No other new instances found — a further sweep of `docs/audit/closure-records.md`
found every other "clean"/"pass" claim already naming its command, count and tree.

**A finding this audit owes against its own conduct, not only others':** this role's PR
#400 audits today (two full passes plus the delta re-audit) put every finding directly
into chat messages to the lead, with no durable artifact filed for either pass until this
record. That is the same dispatch/reasoning conflation §15 names — "reasoning belongs in
a task, a plan, a ruling record or a merged artifact... applies to every role" — and this
auditor's own charter states the same rule independently ("a finding that lives only in
chat is ephemeral"). Named here because auditing others against a rule this session's own
conduct did not fully meet would be exactly the uneven scrutiny the maintainer asked this
audit to avoid.

## The eight lead rulings, verified individually against primary sources

- **R1** (16:47Z, hygiene watch unarmed) — **accurate.** Read
  `/home/puzhenhao1989/w11-handover-2026-08-29/watcher-monitor.sh` directly:
  `REPO=/home/puzhenhao1989/gi-pricing-plan` on line 6, confirming it watches the shared
  checkout, never a member's worktree.
- **R2** (17:02Z, lead-status marker) — **contains a verified 30-minute arithmetic error.**
  States the bad marker's value was "`1788022836`, 17:30:36Z". Independently converted two
  ways (`python3` and `date -u -d @1788022836`, agreeing): `1788022836` is
  **17:00:36Z**, not 17:30:36Z. The underlying point (a future-dated marker existed and
  could silently defeat the staleness detector) is unaffected by which clock-time is
  correct, but the ruling record itself is currently wrong about it and nothing else has
  caught this yet.
- **R3** (17:33Z, reporter derivation) — **accurate.** "Five PRs merged" and "verified
  working, 18:00Z" both check out precisely: PRs #395/396/397/398/399 (the only five
  merged by 18:00Z) match "five" exactly, and PR #400 was still open (first commit
  17:04:12Z, merged 18:54:56Z) at 18:00Z, matching "the executor was mid-gate."
- **R4** (17:47Z, watcher Monitor/poller) — **the original ruling was substantively
  wrong, and says so.** Its own embedded correction ("R4 was wrong in its operative
  instruction, and the watcher corrected it") names the error in its first sentence,
  compliant with §15 even though the ruling it corrects was not compliant with §7's
  presumption of a workable instruction. Its claim that this is "the third time today a
  member has caught the lead... the auditor on the `--extra` string" matches this
  session's own first-hand record exactly (task #50's re-derivation, this session).
- **R5** (17:47Z, gate-in-flight slot) — claims members "have no task tools," matching
  this session's own experience (SendMessage only, no task-board tool used this session).
  The task-board content itself (#56 being inert) is not independently checkable from
  here — noted as unverified, not assumed true.
- **R6** (17:32Z, charter amendments deferred) — references task-board rows (#51/#52/#54)
  this audit cannot read directly. Unverified, not assumed either way.
- **R7** (18:03Z, PR #400 held) — **matches this auditor's own independently-reached
  verdict almost exactly**, including the corroborating detail (the unbridged
  `custom_objective` branch as evidence the `reference_table` bridge was scoped, not
  reflexive) — reached before this audit knew R7 existed, from primary sources
  independently.
- **R8** (18:36Z, Ruling 22 overrides the plan's scope line) — **fully verified against
  the code, not just the account of it.** The original PR #400 (`83dcb59`) has zero hits
  for `compile.py` in its diff (independently re-confirmed); the delta (`5b05a628`,
  committed 18:44:48Z, fifteen minutes after R8's stated pre-review at 18:36Z and ten
  minutes before the 18:54:56Z merge) does modify `compile_bundle()` itself, exactly as
  R8 says it must. The "fails closed, not open" sentinel design and the tripwire test are
  both real, independently run: `test_rate_table_version_row_has_no_status_column` passes
  and asserts against the live SQLAlchemy table, not a comment.

**One filing-hygiene note, minor**: `lead-rulings.md`'s entries run oldest-first (R1
16:47Z through R5 17:47Z) and then reverse to newest-first for the last three (R8 18:36Z,
R7 18:03Z, R6 17:32Z) — R6 at 17:32Z sits chronologically between R2 and R3 but is filed
last. Not a substantive error; a reader scanning for the latest ruling by position alone
would be misled.

## Proposed disposition

Nothing here blocks W11 or reopens a closed work item. Recommend:
1. **R2's timestamp corrected** in `lead-rulings.md` (local, not repo — the lead's file).
2. **A register row** for §7's unassembled instrumentation obligation, on the F26/F-W9-3
   pattern — no owner proposed here, that decision is the maintainer's per this session's
   own established practice.
3. **This record itself stands as the pilot's first §7 data point** (1 audit-fix loop, 2
   auditor passes on Task 1.2, gate re-run independently confirmed), pending whoever next
   revisits the retry-cap numbers.
4. No action needed on §8 — the fix that landed (`4ec7fd1`) is holding; no third
   occurrence found today.
