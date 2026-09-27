---
id: CR-1167
family: closure
kind: review
title: Plan review 14 — the WK-697 close, the register rows decayed to it, and the two downstream Works
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-27
owner: lead
tree: cddf9a6e32e6a780ac93ba769767bb602b054919
phase: P2
work: WK-697
corrected_by: []
relates: [FD-1165, FD-1166]     # ids only — every FD- this closure raised or discharged
---

### Plan review 14 — the WK-697 close, 2026-09-27

**Base tree: `cddf9a6e32e6a780ac93ba769767bb602b054919`** (#822, the W37-11 docs PR, squashed
2026-09-27 15:58:42 BST). **Trigger:** `CLAUDE.md` §14, "at each workstream close". WK-697 was
closed at 2026-09-27 15:25:01 BST by the maintainer's dated line (5), given by delegation (D7,
quoted in `CR-1164` §10 W1). The deputy ruled at 15:04:33 BST that this review is **the first act
after the close, not a gate on it**, and that it is held before the row-9 cleanup. Written by the
lead under `.claude/skills/phase-review/SKILL.md`, started from `date` at 2026-09-27 16:06:28 BST.

**This review is a proposal and binds nothing** until the acceptance line at its foot carries a
date (§14; the skill's first rule). It edits no roadmap row, no plan, and no requirement.

## Scope

WK-697 (RFC-937, one id per governed thing) is closed on `CR-1164`. This review asks whether the
plan still says the right thing now that the Work is real, and disposes of every register row that
has decayed to "the §14 review". It does **not** re-audit WK-697: `CR-1164` did that, with a pass (a)
by an independent auditor (the lead's verdict "CLEAN with dispositions", 2026-09-27 15:35:39 BST).

## Evidence

- **The owed list, generated, not recalled:** `python3 scripts/register-owed.py review`, run at
  `cddf9a6e` on a clean detached copy (`…/tmp/lead-w37-11/rev14-probe`), rc 0: *"22 owed row(s),
  4 matched but excluded as opening with a resolution marker"*.
- **A read-only evidence pass** over those 26 rows. It read each Decision cell, what reviews 11–13
  did with the row, and whether the defect is still present at `cddf9a6e`. The lead holds the table
  it produced; each disposition below cites the file and line that carries the claim.
- `write_runtime_state.py show` at `cddf9a6e` (RFC-895 artifact B), for the §Output citation.
- `CR-1064` (plan review 13) as the form model; `CR-1164`; `docs/roadmap.md`; RFC-937 §8.

## Two corrections to the generated owed list

The skill says the generator's output "is evidence, not authority". Two of its errors change this
review's agenda. Both are filed by the auditor in this PR as **FD-1165**:

1. **F73 is owed but not listed.** The review marker is `re.compile(r"§14")`
   (`scripts/register-owed.py:102`, applied at `:145–146`). F73's cell reads "plan review 14",
   never "§14", although `CR-1164` §8 defers it here. It is added by hand.
2. **F97 and F101 are listed but not owed.** Their current decisions name other events (`CR-1164`
   §8: the charter investigation's first slice, and the create-read-retire audit's first slice).
   They match only because "§14" survives in their superseded opening text. **Not owed; no
   disposition here.**

So **21 rows are owed** here: the generator's 22, less F97 and F101, plus F73. With F28's
residual (below), this review makes **22 dispositions**.

Two further register gaps, filed as FD-1165 limbs (3) and (4):
- **F91 and F93**, whose work item is `—`, were never reached by the per-work sweep behind
  `CR-1164` §8. F93's review-12 routing ("into W37-11's closure record", `CR-1050:96`) was
  dropped by the close. Both are disposed below.
- **F28** is excluded as "Fixed…", but carries residual P5 (`FD-894:648`) with no owner or event.

## Register rows decayed to this review

**Proposed dispositions**, the lead's, per row. Kinds: **(a)** an owner and an event; **(b)** an
accepted deferral with a **new** named event; **(c)** resolved in fact, with its evidence;
**(d)** a finding against the register.

| Row | State at `cddf9a6e` | Proposed disposition |
|---|---|---|
| FR-240/F-W9-3 (clauses 4–6), F27(c), F29 — the gate-coverage cluster | Owned by "the §14 review" (RL-860) since review 11 (`CR-932:55–71`), where three placements were named and none picked. Reviews 12 and 13 moved on. | **(d)** FD-1166. **(a) proposed:** the maintainer names the Work that owns the cluster **in this review's acceptance line**; that line is the event. The lead remains the owner until then. |
| F33 (mypy `files` coverage) | Still present: `pyproject.toml:130–139` lists no `scripts/`. `CR-1164` §8 lists it as "owned elsewhere". | **(a)** Split by cost, as review 11 offered (`CR-932:56,69`). The `files` widening is owned by the lead, and the event is **the first `WK-` maintenance slice after WK-697**. The rest stays with the cluster above. |
| F31 (the watcher's roster derivation) | `watcher.md:26–28` still states the derivation. `:33–40` marks it **UNIMPLEMENTED** and forbids inheriting the constant. Disclosed, not fixed. | **(b)** The charter investigation's first slice (it is a charter clause). |
| F48 (NFR-499 rate limits) | WK-674 is `status: active` (`roadmap.md:649–655`). Review 11 confirmed WK-674 (`CR-932:94–104`), but the cell was never updated. | **(a)** The owner is **WK-674**, and the event is WK-674's map plan. |
| F58 (artifact B had no live writer) | **Resolved in fact.** The watcher now invokes `write_runtime_state.py cycle` each cycle and rewrites on change (RL-907(d)): `position.written_at` = 2026-09-27T14:03:07Z (15:03:07 BST), written when PL-1144 moved to "in progress" (watcher cycle 43). The interim derivation is the deputy's ruling of 11:27:20 BST (FD-1151). | **(c)** Resolved 2026-09-27. The writer is wired and runs each cycle; the source clause is FD-1151's deferred fix. |
| F61 (C2's layer bypassable; no retry counters) | Still present. `scripts/hooks/retry_cap_hook.py:135` reads `retry_counters`; the writer emits none (`write_runtime_state.py:22–24`, whose docstring says the hook "does not exist yet", which is **stale**: the hook exists). Review 13 found the same (`CR-1064:217–225`). | **(b) proposed:** **the residual gap is accepted in writing** (the row's own option (b)), until the charter investigation's first slice wires the counters. The docstring's staleness is added to that event. |
| F63 (reopening a Work close) | Still present; no ruling. "Reopening a Work close is the maintainer's alone." | **(a)** The owner is **the maintainer**; the event is a dated ruling. A plan review cannot discharge this row, so this is stated rather than deferred again. |
| F73 (the reporter's nudge conjunction) | Still present (`CR-1164` §8). Missed by the generator (FD-1165 limb 1). | **(b)** The charter investigation's first slice. |
| F74 (`reporter.md` describes a single-signal nudge) | Still present: `reporter.md:76–83`. | **(b)** The charter investigation's first slice. |
| F75 (the end-turn rule in one charter of seven) | Still present: the rule is in `executor.md:69` only. | **(b)** The charter investigation's first slice. |
| F86 (RL-909's decay rule has no faithful check) | Still present (`CR-1164` §8). | **(b)** The create-read-retire audit's first slice. FD-1166 is its newest instance. |
| F89 (test fixtures written into the real `docs/plans/`) | Still present: `tests/test_audit_docs_finding_citations.py:51`. | **(a)** The owner is the lead, and the event is **the first `WK-` maintenance slice after WK-697**. It is a small tmp-corpus fix and does not need the audit. |
| F90 (check 37's heading detector) | Option B's residue remains (`CR-1164` §8). | **(b)** The create-read-retire audit's first slice. |
| F91 (artifact B's writer not running) | **Resolved in fact**, on the same evidence as F58: the writer ran at 14:03:07Z. Its position is correct for the tree it read (PL-1144 was "in progress" until this PR). | **(c)** Resolved 2026-09-27. It was missed by `CR-1164` §8 (FD-1165 limb 3). |
| F93 (RFC-937 §1.5 vs the vendored-manifest exemption) | Still present: RFC-937 `:380` says "vendored skills get `vendored: true` + `origin:`". | **(a)** The owner is **the maintainer**, and the event is a dated RFC-937 amendment line. Review 12's routing was dropped (FD-1165 limb 3). |
| F94 (the ruling-heading census predicate) | Carried as it stood by `CR-1065:437`. | **(b)** The create-read-retire audit's first slice. |
| F96 (a ruling without `## Ruling N` migrates as `PL-`) | No guard found. | **(b)** The create-read-retire audit's first slice. The migration-time urgency is moot now that the migration has run. |
| F113 (spawn against a `draft` plan) | "The mechanical gap is explicitly not closed" (`CR-1164` §8). | **(b)** The next `delivery-process.md` amendment (a spawn guard is a process rule). |
| F114 (four frozen plans state row (d) in a superseded form) | Limb 1 not met: `PL-939:71–73` and `PL-960:338` are unannotated. Frozen plans take corrections only through an `RL-` or `RFC-` (check 34). | **(b)** The create-read-retire audit's first slice, which will carry the correcting `RL-`. |
| F28 (the RFC-840/841 adoption pilot), excluded as "verify" | Residual **P5** (`FD-894:648`, the stand-down procedure) has no owner or event. P7 and P1b's working-note half are not evidenced as landed. | **(b)** P5, P7 and P1b go to the charter investigation's first slice, which verifies P7 and P1b first. FD-1165 limb 4. |
| F87, F88, F92, excluded as "verify" | Each opens "Resolved 2026-09-27" with its evidence (`CR-1164` §8); F92's 18-file residual has its event. | **Covered; no residual owed here.** |
| F97, F101 | Not owed (see the corrections above). | — |

**Owed: 21 rows, plus F28's residual. Disposed: 22 of 22.** By kind: **(a)** 5 (F33's widening,
F48, F63, F89, F93); **(b)** 12 (F31, F61, F73, F74, F75, F86, F90, F94, F96, F113, F114, F28);
**(c)** 2 (F58, F91); **the cluster**, 3 rows (FR-240/F-W9-3 clauses 4–6, F27(c), F29): **(d)**
FD-1166, with an **(a)** event (the acceptance line). 5 + 12 + 2 + 3 = 22. The limbs of FD-1165 cover the generator's gaps. **The register cells are
updated to these dispositions by the auditor after this review's acceptance line is given**
(FD-1166: a disposition that never reaches the register is how these rows decayed three times).

## 1. Completion — derived, never recalled

**No change; not re-derived.** `CR-1164` is a fresh completion audit of this Work, hours old. An
independent pass (a) re-derived its figures on detached copies, and its delta read confirmed the
final head (the lead's verdict of 15:35:39 BST). Re-deriving the same sources here would confirm
nothing (the skill: "If a fresh audit has just covered this, say so and move on").
`scope-audit.py` and `req-coverage.py` measure module specs; WK-697 changed governance documents
and instruments, not a module's requirements, so neither applies.

## 2. Omission — what would nobody notice was missing?

**Finding: the two downstream Works that hold most of the deferred work have no `WK-` row.**
RFC-937 §8's closing sentence and the roadmap's WK-697 text (`docs/roadmap.md`, the WK-697 row)
name them: **"the charter investigation"** (§1.6 made binding in each charter, with a
directory-level `owner:`) and **"the create-read-retire audit"** (the process step per transition in
§1.2's state machines). At `cddf9a6e`:
- `git grep -c -i -E 'create-read-retire audit|charter investigation'` gives **24** matching lines
  in `docs/findings/register.md` and **41** in `CR-1164`, each naming one of them as the event
  a deferral waits on;
- `docs/roadmap.md` names them in prose on one line and gives neither a `WK-` id, a row or a
  status.

An event that belongs to a Work nobody has minted cannot fire. The deferrals are real and owned
(the lead), but their trigger is a name, not a row. The same shape is what FD-1166 records for
the older rows.

The generator's blind spots (FD-1165) are the second omission: three rows owed here (F73, F91,
F93) were invisible to the tool the close relied on.

## 3. Skills and research — the gap analysis

- **`phase-review`'s §Output requires the retry counters** (RFC-895 artifact B), and they still do
  not exist: `write_runtime_state.py show` at `cddf9a6e` has no `retry_counters` block, by the
  writer's design (`:22–24`, "Absent, never zero"). That is the second review in a row to find
  this (review 13, `CR-1064:217–225`). The docstring's reason is now stale (the hook exists,
  `scripts/hooks/retry_cap_hook.py`). **Proposal:** carry it with F61 (above), so the skill's
  clause is satisfiable when the counters are wired. **No skill edit in this review.**
- **`doc-id-migration-run`** gained its guard line in #821 (the C4 guard); its `Verified` date was
  refreshed there. **No change.**
- **No external skill is proposed; none was installed.**

## 4. Document drift

**No new drift beyond what `CR-1164` already deferred with owners:**
- `delivery-process.md:282`'s stale checklists pointer, with the check-27 / verify-pin dual field
  (FD-1154);
- `document-ids.md` §1.9's non-existent SL- PR-title lint (FD-1163 limb (c));
- the auditor charter's essay path (FD-1153);
- the watcher charter's unnamed source (FD-1151).
One new item: **`write_runtime_state.py:22–24`'s docstring** says the counter hook "does not
exist yet"; it exists. It is carried with F61 (§3). The roadmap was brought current by #822 (the
WK-697 row closed; the #757 correction). **No change proposed to any spec.**

## 5. Shape — is the cut still right?

WK-697 closed as planned (W37-1…W37-11). **One proposal, for the maintainer:**

**Proposal 5.1: mint the two downstream Works as roadmap rows**, the charter investigation and
the create-read-retire audit, each with a `WK-` id, so that the deferrals in the register and in
`CR-1164` wait on a row with a status rather than on a name. This is a roadmap change only
(`CLAUDE.md` §0's table: a later capability is a spec change, never code now). Their contents are
already enumerated in `CR-1164` §10's "taken over" list and in this review's dispositions.
**Recommendation: accept**; the alternative is re-listing the same deferrals at review 15.

## Output

- **Retry counters (RFC-895 artifact B):** none exist at `cddf9a6e` (§3). Question 5 has no pilot
  data to answer against; **no change** because of it.
- **Proposals needing the maintainer's line:**
  1. the cluster's owning Work (FR-240/F-W9-3 clauses 4–6, F27(c), F29);
  2. F63's ruling, and F93's RFC-937 amendment (owner: the maintainer);
  3. F61's residual gap, accepted in writing;
  4. Proposal 5.1.

## Verdict

Every row decayed to this review has a disposition (22 of 22: 21 owed rows and F28's residual), and every question has a written
answer. Two findings are filed alongside (FD-1165, FD-1166). **Nothing here binds until the
acceptance line below carries a date.**

## Sources

- `python3 scripts/register-owed.py review` at `cddf9a6e` (a detached copy), rc 0.
- `write_runtime_state.py show` at `cddf9a6e`.
- `CR-1164` (§8, §10); `CR-1064` (review 13, `:139–144`, `:217–225`); `CR-1050` (review 12,
  `:70–72`, `:96`); `CR-932` (review 11, `:52–140`, `:288–294`); `FD-894:648`.
- `scripts/register-owed.py:102`, `:145–146`; `scripts/hooks/retry_cap_hook.py:135`;
  `.claude/roles/watcher.md:26–40`; `.claude/roles/reporter.md:76–83`; `executor.md:69`;
  `pyproject.toml:130–139`; `tests/test_audit_docs_finding_citations.py:51`;
  `docs/roadmap.md:649–655`; RFC-937 `:380` and §8.
- `.claude/skills/phase-review/SKILL.md`; `CLAUDE.md` §§0, 12, 13, 14; the deputy's rulings of
  2026-09-27 15:04:33 and 15:32:22 BST.

**Maintainer acceptance:** quoted verbatim from the deputy's entry *"PLAN REVIEW 14 acceptance RE-ISSUED"* (written 2026-09-27 16:20:35 BST; the decision and its time, 16:18:24 BST, unchanged; it supersedes only the wording of the 16:18:24 entry), committed by the lead as this record's follow-up:

**Maintainer acceptance by delegation (deputy, on the maintainer's instruction of 2026-09-26 17:02:52 BST), given under the plan-review standard of CLAUDE.md — the rule that a review carries "an explicit maintainer acceptance line with a date" (its section fourteen):**
- **2026-09-27 16:18:24 BST — CR-1167, plan review 14 at the WK-697 close, is ACCEPTED** as read by me at `w37-11-close` `77c1d7eb` (`kind: review`, lead-authored; the five plan-review questions answered against the real work; 22 of 22 decayed rows dispositioned — 21 owed rows and F28's residual; FD-1165 and FD-1166 filed alongside). Its recommendations are proposals and bind nothing beyond this line (the plan-review standard: "the output is a proposal, never a change"); it edits no roadmap. On the four items its §Output puts to this line:
  1. **The gate-coverage cluster (FR-240 / F-W9-3 clauses 4–6, F27(c), F29): owner the create-read-retire audit Work; event its first slice.** The cluster is about what the instruments cover, which is that Work's subject; the register cells carry that owner and event, with FD-1166 as the finding that names the decay.
  2. **F63 (reopening a Work close) and F93 (RFC-937 §1.5 against the vendored-manifest exemption): deferred with the MAINTAINER as owner**, events a dated ruling and a dated RFC amendment respectively — not decided by delegation: a reopen rule and an RFC amendment are the maintainer's own design points, and neither blocks today's close. The register cells read "owner: maintainer; event: the maintainer's dated line".
  3. **F61's residual gap (C2's layer bypassable while the retry counters are absent): ACCEPTED in writing**, as the review proposes; owner the lead; event plan review 15, where it is re-read against artifact B's counters if they exist by then.
  4. **Proposal 5.1 (mint the two downstream Works — the charter investigation and the create-read-retire audit — as `WK-` roadmap rows): ACCEPTED as a proposal.** It is the right shape (an event that belongs to a Work nobody has minted cannot fire; a roadmap-only change under CLAUDE.md's phase table in its section zero). **Its execution is not today's:** it is the first act of the next session — one roadmap-only PR minting both rows with ids from `next --ref HEAD`, their contents by reference to CR-1164 §10 and CR-1167's dispositions, my ACK — recorded in the handover so the maintainer's order of 21:16:14 (cleanup, then power off) is not extended by re-planning. Until then every "first slice of the charter investigation / create-read-retire audit" event names the Work by that phrase.
- The maintainer's later line overrides this one.
