# Audit record — nt-0012-0013-0014-adoption (`docs/audit/checklists/work-item-close.md`)

> Not a `CLAUDE.md` §13 numbered-workstream closure — NT-0012, NT-0013 and NT-0014 are notes
> under `.claude/notes/`, not a roadmap `W`-id, and this Work closes under the maintainer's
> 2026-08-30 delegation (`docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md` §1.1), not
> under `CLAUDE.md` §13's own acceptance line. It follows `work-item-close.md`'s checklist
> because the lead asked for it in that shape, and because the checklist's own sections —
> derive scope, evidence with its tree, one verdict per unevidenced item — are the right
> discipline regardless of which authority accepts the result. Same framing as the precedent
> record, [`nt-0010-0011-adoption`](../nt-0010-0011-adoption/README.md).

## Scope

**The plan**: `docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md`, filed against
`origin/main@2e4684b`. Eight slices, per its §2 table (A, B, C, D, E, F, G, plus the rulings
that re-cut G and dissolved its C3 half):

| Slice | Content | Commit | PR |
|---|---|---|---|
| A | `§12`→`§15` fix, process core JSON filed | `33b5ef1` | #448 |
| B | Check 26 — process-core citation-drift check, inside `scripts/audit-docs.py` | `0be9c3c` | #451 |
| C | NT-0012's two rules given durable homes (Rulings A1, A2) | `97965be` | #456 |
| D | NT-0013's "remove the relay" (Ruling A3) | `97965be` | #456 |
| E | Runtime state file — NT-0014 artifact B | `b551060` | #506 |
| F | Plan validator C1 — check 28, `writing-plans` acceptance-standard field | `26de823` | #510 |
| H | Process-core digest — check 27 | `53257b4` | #513 |
| G | C2, the retry-cap hook (C3 dissolved, not built — Ruling 40 §3) | `9e8783d` | #516 |

All eight are merged on `origin/main`, confirmed at `9e8783d` (this audit's own tree,
`git log --oneline origin/main -20`). C3, the verify-gate hook originally paired with C2 in
the plan's slice G, was **dissolved by Ruling 40** §3
(`docs/plans/2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md:189-207`) — verified
directly, not assumed from the lead's relay: the ruling's own text reads *"it is not built, in
either form, and the row is closed as discharged rather than deferred"* on the ground that CI
already runs a stronger, unbypassable check on every pushed branch, while a local or git hook
would check a weaker thing and can be silently skipped. Confirmed on disk: no `.claude/hooks/`
directory, no git-hook wiring (`git config --get core.hooksPath` unset), and C3 named nowhere
in `scripts/hooks/`.

**§1.1 delegation, verified against the plan's own text rather than the lead's paraphrase**:
the plan quotes the maintainer verbatim — *"authorise you to approve NT-0012 NT-0013 and
NT-0014 landing on behalf of me"* — and scopes it explicitly to landing these three notes,
**not** W11's close, W12, or any later phase. That is what §1.1 says; the lead's relay matches
it.

## Checklist

Ran against `close-workstream`'s current text (this session's own edit added one new §3
subsection and a Verified entry, both after the audit below; neither changes a verdict). Both
gate halves run locally (§2): `uv run ruff check .`, `uv run mypy` (173 source files clean at
`9e8783d`), `uv run lint-imports`, `python3 scripts/audit-docs.py` (clean, including checks
25–28), `uv run python scripts/req-coverage.py` (clean). **Full `uv run pytest -q` was not
re-run in this audit** (out of scope per the lead's brief — CI ran it green on every merged
commit); `--collect-only` was run instead, twice, to reconcile the disputed count (§ below).
Frontend half not touched by any of these eight commits (all `git show --stat` confirm no
`frontend/` paths) except where a PR's own test plan already ran it (F, #510: 602 frontend
tests, clean) — no frontend gate re-run needed for the others.

Each new check proven on deliberately broken input, per §3: see Evidence below, one row per
slice, each citing where the mutation proof lives and which of the four I re-ran myself.

Root `README.md` pointer freshness: unaffected — none of its pointers (`docs/roadmap.md`,
`docs/process/delivery-process.md`) resolve to a different location as a result of this close.

`CLAUDE.md` §14 phase-review trigger: **not raised by this record.** The checklist's own
instruction is to confirm with the planner whether one is due; NT-0012/0013/0014 is a Work
under a note-adoption process, not a numbered workstream, and plan review 10 already ran at
W11's second close the same week — flagging for the lead to confirm with the planner rather
than assuming either way.

## Evidence

### Slices A, B — already accepted, re-confirmed rather than re-audited

Plan §4 records both accepted 2026-08-30 under the delegation, each with "clean gate" (A) or
"clean gate + six-mutation proof with a silent negative control" (B). Re-confirmed live: A's
`§12`→`§15` fix is on disk at `CLAUDE.md`/`delivery-process.md` as described; B's check 26 is
present in `scripts/audit-docs.py` and its six-mutation table is reproduced in PR #451's own
body (§99 citation, §5.99 step-count, `authoritative: true`, missing `derived_from`, a
non-`§`-citing source, and a deleted-extract-with-§10-still-required case — each with the
exact failure string named), plus a silent negative control (unmutated tree passes). Not
re-run by hand in this audit; the six-case table plus check 26's presence in the current
green `audit-docs.py` output is treated as sufficient re-confirmation for an already-accepted
slice. **Verdict: accepted, carried forward** (no new evidence needed).

### Slices C, D — Rulings A1–A3, verified landed exactly as ruled

- **Ruling A1** (credential-lifetime rule → `secret-hygiene`): confirmed at
  `.claude/skills/secret-hygiene/SKILL.md:35`, heading *"A credential in a job directory is
  borrowed, not stored (NT-0012)"*.
- **Ruling A2** (search-by-shape rule → `close-workstream`, beside "A false zero argues"):
  confirmed at `.claude/skills/close-workstream/SKILL.md:310`, heading *"Search for the
  thing's shape, not its container's name (NT-0012)"*.
- **Ruling A3** (NT-0013's "remove the relay" → `delivery-process.md` §15, after the existing
  "verify against the primary source" bullet): confirmed at `docs/process/delivery-process.md
  :315,326-332` — the existing bullet at `:315`, the new one immediately after at `:326`,
  heading *"Remove the relay, do not merely distrust it (NT-0013)"*.

**Verdict: delivered and tested** (each ruling's own text is the acceptance criterion; each
landed verbatim where ruled).

**Finding, not in the lead's brief, found independently**: both `.claude/notes/0012...md` and
`.claude/notes/0013...md` still carry `Status: open` at `9e8783d`, unchanged since they were
raised — even though the rules each note asked for are now built and landed. `.claude/notes/
README.md`'s own definition of `open` is *"Raised, assessed, not agreed... nothing is
built"*, which is no longer true of either. Same shape NT-0014's own note hit and was
corrected for (2026-08-30, by the lead, "only the party that changed the facts can verify
it"). Not fixed in this record — note-status ownership is the lead's/maintainer's per each
note's own `Owner` field, not the auditor's write scope. Filed as a Finding below.

### Slice E — artifact B (runtime state file)

`.claude/skills/watcher-runtime-state/scripts/write_runtime_state.py`, 10 tests including
Ruling 47(d)'s acceptance test (a no-op cycle produces a byte-identical file, verified failing
by hand against a scratch mutation before confirming it passes against the real
implementation — PR #506's own test plan). **Verdict: delivered and tested**, with one
already-filed carried finding, **F58** (`docs/audit/register.md`): no live process invokes the
script on a schedule, so `watcher.md`'s "each cycle" claim does not hold today. Re-confirmed
live in this audit: `python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py
show` reports no runtime state file exists at `~/gi-pricing-plan.local/handover/
runtime-state.json` — F58 is current, not stale.

### Slice F — check 28, plan-acceptance-standard validator

`scripts/audit-docs.py` check 28, `tests/test_audit_docs_plan_acceptance_standard.py` (4
permanent cases). Broken-input proof from PR #510's own test plan: a synthetic plan dated
after the 2026-08-31 cutoff with no heading reds and names the file; a legacy plan (before
cutoff) with no heading passes into the aggregate note; a conforming plan passes. Re-confirmed
live: this audit's own `python3 scripts/audit-docs.py` run reports *"98 legacy plan(s) filed
before 2026-08-31 exempted... check 28: 1 plan(s) filed on/after 2026-08-31 checked"* — the
cutoff and exemption count are both live and correct, not asserted from the PR body.
**Verdict: delivered and tested.**

### Slice H — check 27, process-core digest reconciliation

`scripts/audit-docs.py` check 27, `tests/test_audit_docs_process_core_digest.py` (4 tests: a
byte change reds; a missing digest reds; an unrelated-file edit stays green (negative
control); the committed tree stays green (positive control)) — PR #513's own test plan.
Re-confirmed live: `python3 scripts/audit-docs.py` reports check 27 green, digest matching.
**Verdict: delivered and tested.**

**Finding**: `meta.verified_against_tree` is set to `79991f36c3337b87a2ae788acae3c255d5ae1084`
— H's own base commit, one merge before H's own edit to the spec bytes the digest covers, and
G's later re-reconciliation (which also edited `delivery-process.md`) carried the same wrong
value forward rather than correcting it. Check 27 validates the digest, never the SHA, so this
produces no failure anywhere and the field is currently harmless — content-correct, wrong
citation. Written up as a `close-workstream` skill addition (§ below) rather than a register
row: it is process guidance for the next author, not an open defect with an owner, since the
citation self-heals on the next edit to `delivery-process.md`.

### Slice G — C2, the retry-cap hook (C3 dissolved)

`scripts/hooks/retry_cap_hook.py`, two entry points (`record`, `hook`) sharing one decision
function `_would_breach`. `tests/test_retry_cap_hook.py`, 11 cases. **Spot-checked myself**,
per the lead's request, rather than only citing the PR: mutated `_would_breach`'s
`current >= cap` to `current > cap` at `retry_cap_hook.py:148`, re-ran the suite — **4 of 11
cases failed**, matching PR #516's own reported figure exactly — then restored the file byte-
for-byte and re-ran (11/11 pass). `record`'s and `hook`'s shared use of `_would_breach`
(`:213`, `:311`) confirms the lead's claim that `record`'s refusal is unconditional and
independent of hook wiring — both paths compute the same breach decision, and `record` never
depends on the `PreToolUse` registration to enforce it. **Verdict: delivered and tested** on
its own stated claim.

**The substantive gap** (the lead's framing, verified rather than assumed): Ruling 40 §3
dissolved C3 because a Claude Code/git hook is bypassable (session-disabled hooks, an
uninstalled or `--no-verify`-skipped git hook) **with CI sitting behind it as a stronger,
unbypassable backstop**. §4 of the same ruling approves C2 as a hook on the ground that it
intercepts an action no artifact records — true, and it is why C2 needs to be a hook at all —
but §4 never asks whether C2's *own* registration point is bypassable the same way, and it is:
`.claude/settings.json` is disableable per-session and overridable by the gitignored
`.claude/settings.local.json`, and — unlike C3 — **nothing re-derives `retry_counters` from a
durable artifact**, so there is no CI-equivalent backstop behind it. PR #516's own body names
both escape hatches in the same sentence it uses to distinguish C2 from C3, and
`delivery-process.core.json:249`'s design note says the same thing in the artifact itself.
Filed as **F61** below. What genuinely mitigates, and is why this is not "the same defect as
C3": `record()`'s refusal is unconditional and mutation-proven independent of the hook path
(confirmed above), which C3 never had — C3's *only* enforcement was the bypassable hook
itself.

### Test-count discrepancy — resolved, not re-litigated

PR #516's own test plan reports 2436 (measured pre-rebase, on a tree that ceased to exist once
the branch rebased over slice H). **Verified independently in this audit, both at fresh
`uv sync --all-packages` worktrees**: `origin/main` immediately before slice G
(`79991f3`) collects **2429** tests; at `9e8783d` (slice G merged, this audit's own tree) it
collects **2440**. CI ran the full suite on the actual merged branch tip, `d7cb4f6` (per
`gh run list --branch feat/nt-0014-slice-g-c2-retry-cap-hook`: both `docs` and `python`
workflows `success`), so the merged tree is verified — only the PR body's self-reported number
was stale. **2436 does not appear in this record as a live figure.**

### Ruling 48's citation — cosmetic, verified

`delivery-process.md:110-113`'s §6 step 4 parenthetical currently reads *"(rulings record:
`docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md`, Ruling 48, closing Part C row 5)"*,
where Ruling 48's own ruled text read `(Ruling 40)`. **Reworded, not wrong**: Ruling 48 is the
ruling that actually wrote this replacement sentence (closing Part C row 5), so citing Ruling
48 rather than Ruling 40 — which the sentence's *content* still credits by name in-body ("CI
runs the full gate...") — is arguably more accurate, not less. The body text after the
parenthetical is **verbatim** against Ruling 48's ruled replacement, confirmed word-for-word.
No finding filed.

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| F61 (new) | C2's `PreToolUse` registration is bypassable the same way C3's git hook was, and unlike C3 has no CI-equivalent backstop — Ruling 40 never reconciled its own §3 and §4 against each other | carry forward with an owner — build the re-derivation cycle (Ruling 47(b)) or have the lead/maintainer explicitly accept the residual gap; no slice names this today | closed-with-findings |
| F57 (amended) | §7 retry-cap instrumentation — slice G landed, giving the counter a writer, but zero fix/replan cycles have run through it yet | amended in place; stays open until a live workstream runs under it | closed-with-findings |
| F33 (noted) | `scripts/audit-docs.py` now carries checks 25–28, still outside `[tool.mypy]`'s `files` (10 real errors when run directly, confirmed live) | note added; disposition unchanged, still owned by the §14 review bundling F27(c)/F29/F33 | closed-with-findings |
| F58 (re-confirmed, not new) | Artifact B has no live scheduled writer | unchanged; re-confirmed current at `9e8783d` | closed-with-findings |
| NT-0012/0013 `Status: open` (new, unfiled) | Both notes' rules landed (slices C, D) but their own `Status` fields still read `open`, contradicting `.claude/notes/README.md`'s definition | not the auditor's write scope (each note's `Owner` field names the lead/maintainer); flagged in this record and in the report to the lead rather than filed as a register row, since it is a one-line note correction, not a workstream-scale gap | open — needs the lead to correct both notes' `Status` fields |
| C2/C3 test-count (2436 vs. verified 2429→2440) | Stale self-reported PR figure, pre-rebase | resolved by this audit's own `--collect-only` runs at both trees; no fix needed, no further action | closed |
| Ruling 48 citation reword | Cosmetic | accept — body verbatim, citation arguably improved | closed |
| `meta.verified_against_tree` set at authoring time (habit) | Not a defect today (digest is content-correct); citation points at the wrong commit and would mislead a future `git diff` instruction | recorded as a `close-workstream` skill addition and Verified-log entry, not a register row (self-healing on next spec edit) | closed |

## Not delivered by this adoption

- **C3** — not delivered, **deliberately**: dissolved by Ruling 40 §3, discharged rather than
  built. `delivery-process.md` §6 step 4 carries the ruled replacement text.
- **The re-derivation/CI-equivalent backstop for C2** (Ruling 47(b)) — not built, no owner
  named until this record's F61.
- **A live scheduled invocation of artifact B's writer** — not built, F58, unowned-pending-
  authorisation (pre-existing, re-confirmed here).
- **A §7 retry-cap threshold revisit** (≤1/≤2) — cannot happen yet; zero cycles of live data
  exist even though the counter now has a writer (F57, amended).

## Sign-off

Auditor verdict per slice: **A, B — accepted (carried forward, unchanged). C, D, E, F, H, G —
delivered and tested**, each with the findings named above carried forward rather than
blocking. **C3 — correctly not delivered** (discharged by ruling). No slice is proposed
`fix before close`.

**Acceptance of this Work close is the lead's**, under §1.1's delegation, per `CLAUDE.md` §12
— left undated and unsigned here for the lead to complete.

Lead acceptance: _____________________ Date: _____________

---

**Accepted by the lead, 2026-08-31**, under the adoption record's §1.1 delegation of the
maintainer's acceptance authority. The auditor's verdicts above are **adopted unamended**, and
its satisfaction is stated in its own words in this record.

**What this close does not claim.** **F61 is open and unowned**: C2's `PreToolUse` layer is
bypassable in exactly the way Ruling 40 disqualified C3's git hook for — session-disabled
hooks, a gitignored `settings.local.json` — and **unlike C3 there is no CI-equivalent
backstop**, because nothing re-derives counts from artifacts. C2 therefore inherits C3's
disqualifying defect without C3's saving grace, and Ruling 40 never reconciled the two. What
genuinely mitigates it, and is not nothing, is that `record()`'s own refusal is unconditional
and mutation-proven independent of hook wiring — which C3 never had. **The gap needs a decision:
build the re-derivation cycle, or accept it explicitly. It is not discharged by having been
disclosed.**

**F58 and F57 are likewise open**: artifact B has no live writer, and no retry-cap cycle has
run, so `delivery-process.md` §7's caps remain in force with none of the instrumentation their
own adoption was conditioned on. **The adoption built the mechanisms; it did not start them.**

**One correction this close prompted.** NT-0012's and NT-0013's own `Status` rows still read
`open` while their rules had been in force since `97965be`, and NT-0014's read `accepted` after
its last slice merged. All three are corrected to `landed` — found by the auditor, outside its
write scope, and fixed here rather than left for a reader to trip over.
