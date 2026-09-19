---
id: CR-1065
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: W37-6 (WK-697 slice 6) — checkpoint 3 close
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-18
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: a0dbd20a1b276028e9a84647fd17f2a28213627f
phase: P2
work: WK-697
corrected_by: []
relates: [FD-1024, FD-1066, FD-1067, FD-1068, FD-1069]
---

# CR-1065 — W37-6 checkpoint 3 close

## 0. Provenance and governance of this record

This record is drafted by the executor from **the auditor's evidence report**
(`~/gi-pricing-plan.local/handover/auditor-w37-6-cp3-report.md`, tree `4d9fe1d`, cited below
as "auditor report, §N") and **the lead's verdicts**, issued in the checkpoint-3 brief and
reproduced verbatim in §1 below. It re-measures every item the lead marked
**delivered-but-untested**, per `CLAUDE.md` §13 ("every requirement without evidence gets one
of four verdicts... the verdict is the main thread's, never a subagent's" — here, the lead's,
recorded by the executor). **The executor issues no verdicts of its own**; §1's verdict column
is the lead's, with the re-measure result substituted where the lead asked for it.

**Checkpoint-3 governance, ruled by the deputy 2026-09-18 00:55:09 BST** (`to-lead.md`, quoted
in full): checkpoint 3 is governed by `CLAUDE.md:283` ("A Slice is not [accepted by the
maintainer]: it closes on a clean audit and the lead's merge"), not by the stricter wording at
`PL-1058:37-38` — corrected in the same PR as this record, see
`docs/plans/PL-01058-w37-6-migration-run-ledger.md`'s dated correction. **Checkpoint 3 is met
when:** (1) the close-workstream checklist is clean on the auditor's evidence and the lead's
four verdicts, with every delivered-but-untested item re-measured before this record is cut —
a failing re-measure moved to deferred-with-owner, dated, never silent (this record does
that, §1 and §2); (2) this PR (close record + roadmap row + ledger) is gated, CI green, and
merged under the deputy's merge-ACK; (3) review 13 (`CR-1064`, PR #786) is filed as a
proposal with its acceptance line pending (already merged to `main` as `ce808d7`, ahead of
this record — not this PR's to do). The pending
acceptance lines on reviews 12 and 13 are reported to the maintainer as open and binding nothing
(`CLAUDE.md` §14).

## Scope

### 1. Scope, and the checklist's disposition

Scope is derived from `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`,
Slice W37-6 (`:667-733`); `docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md`'s 14-item
Acceptance Standard (`:71-162`); and RFC-937 (`docs/rfcs/RFC-00937-...md`) §7 (a)-(i) (W37-6's
own — (j)/(k) are W37-11's, per the corrected split, auditor report §1a). The tables below
reproduce the auditor's evidence (§1a-§1c of the auditor report) with the lead's verdicts
substituted, and the executor's re-measure result where the lead asked for one.

### 1a. Map plan preconditions (P1-P6)

| # | Item | Auditor evidence | Lead's verdict |
|---|---|---|---|
| P1 | DP-1/2/3 resolver ids | Rulings 66/67/68 | evidenced |
| P2 | Full-class sweep landed, attached to leaf plan | PL-960 §10/§6 | evidenced |
| P3 | `gh pr list --state open` empty | not independently re-checked this session | evidenced — standing verify (the ledger's PR sequence merged sequentially; no open PR contradicts it) |
| P4 | `git branch -r` = `origin/main` only | not re-run | evidenced — standing verify |
| P5 | `git status --porcelain` empty | this worktree: empty | evidenced (this worktree) |
| P6 | Maintainer's dated go-ahead | RL-1049 | evidenced |

P3/P4 measured now as history, per the brief: the lead's verdict is "evidenced (standing
verify + ruled table RL-1046 D5)" for the pair (P3/P4 here; items 4 and 6 below carry the
same disposition).

### 1b. Leaf plan's 14-item Acceptance Standard, and RFC-937 §7 (a)-(i)

| Item | RFC-937 §7 row | Auditor evidence (summary) | Lead's verdict | Re-measure (this record) |
|---|---|---|---|---|
| 1 (a) Classification | (a) | 489 = 489, 0 `none` | **EVIDENCED** (fresh run) | Not re-run separately; auditor's fresh run stands |
| 2 (b) Sequence integrity | (b) | exit 0, contiguous | **EVIDENCED** (fresh run) | as above |
| 3 (c) Index byte-stability | (c) | "OK (byte-stable)" | **EVIDENCED** (fresh run) | as above |
| 4 (d) Legacy-form sweep | (d) | 5460 hits (516 fatal, 4944 disclosed), no FAIL row | **EVIDENCED** (standing verify + RL-1046 D5) | not re-injected this record either; carried on the standing verify |
| 5 (e) No padded id in prose | (e) | check 32 clean; `test_audit_docs_check_32_disposition.py` 5/5 | **EVIDENCED** (fresh run) | as above |
| 6 (f) No product identifier moved | (f) | `EXPECTED_VERDICTS["f"]=PASS`, RL-1044 | **EVIDENCED** (standing verify + RL-1046 D5) | own `git grep -c 'VR-DST-1'` not re-run this record either; carried on the ruled table |
| 7 (g) Script touched only headers/tokens | (g) | standing FAIL; g1 clean, g2 `classified-by-none`=251/971 | **DEFERRED WITH OWNER — W37-11**, `#757` first item | see §3 NFR table — unchanged, standing red, fully disclosed |
| 8 (h) Full gate green | (h) | `audit-docs.py`/`req-coverage.py` clean; CI green on `71f5a22` (4 runs); mypy/pytest/pnpm not re-run at that session's tree | **EVIDENCED** — gate 13/13 on `f777159` (tree == `71f5a22`'s), `handover/gate-f777159/gate.log`, + main CI ×4 on `71f5a22` (run ids `35268549712`/`35268549550`/`35268549539`/`35268549620`); **and the full local gate on `03e1cb0`** (tree == `ce808d7`, this PR's base, run 2026-09-18 01:26:49): 13/13, `3436 passed, 3 skipped, 1 xfailed` (collected 3440 == ran 3440) — mypy, pytest, pnpm and `generate-contracts.py --check` all included, superseding the "not re-run" reading below | Local re-run this checkpoint: `python3 scripts/audit-docs.py` exit 0, `uv run pytest -q tests/test_audit_docs*.py tests/test_doc_id.py` — see §4. **#787's own gate on its final head:** this PR's own gate on `30221dd`, the record's content head (`handover/gate-30221dd/gate.log`: 13/13, `3441 passed, 3 skipped, 1 xfailed`, collected 3445 == ran 3445, GATE END 2026-09-18T01:20:23Z); the final commit adds only this line (deputy ruling, the bounded form of to-lead.md:3851) |
| 9 Scan-roots guard re-derived | — | `test_a_missing_notes_root_fails_the_audit` 1/1; 5-path mutation not re-run | **EVIDENCED** (fresh run) | as above |
| 10 Widened scope = stamped set | — | check 30: 446/66 F83 skips, not cross-checked against §4 step 5 set | **EVIDENCED** (fresh run) | as above |
| 11 Every derived instrument load-bearing | — | not re-run by either session | **re-measured before the cut** | **RE-MEASURED, HELD.** See §2.1 — fires exactly as the discriminating form requires |
| 12 Requirement-facing proof (W37-7) | — | W37-7 not started | **not started — W37-7's, not W37-6's** | unchanged |
| 13 Vendored exemption reaches only blanket passes | — | not re-run | **re-measured before the cut** | **RE-MEASURED, HELD** for the files-beneath-a-manifest population — the two corrupted `.ps1` scripts are FIXED BEFORE CLOSE by PR #788 → main `a8b3c39`; the manifests' own rewrites are by design (RL-990 item 3). See §2.2 — the two named §5.4 content edits **REASSIGNED to W37-7**; the sweep-reaches-vendored mechanism gap filed as **F111, owner W37-11** |
| 14 Three W37-4 deferrals discharged | — | not independently re-confirmed | **re-measured before the cut** | **RE-MEASURED, PARTIALLY HELD.** See §2.3 — one confirmed by symbol, one discharge-mechanism mismatch found, one no in-tree fixture test found; moved to **deferred with owner, lead/W37-11** |
| (i) Every H row in §5 closed by a named commit | (i) | not walked row-by-row | **re-measured before the cut** | **RE-MEASURED, PARTIALLY HELD.** See §2.4 — 56 H/H+M rows sampled; 49 closed within W37-6's own commit chain, 6 not closed (still carrying pre-migration content), 1 path does not exist, 1 correctly excluded by design. Each of the 7 gaps **REASSIGNED per file** to the slice owning that area (W37-7/8/9/10); W37-11 owns the fuller (i) walk itself |

Items 1-6, 9, 10: the lead's verdict of EVIDENCED stands; this record did not re-run every one
of them a second time (the brief scoped fresh re-measurement to items 11, 13, 14, (i) and F87,
plus what item 8 needed locally — §4 below reproduces that local run's exit codes). Item 7
(row g) is unchanged: still a standing, disclosed FAIL, per CR-1063 §6, deferred to W37-11 with
`#757` as its first item.

## Evidence

### 2. Re-measures

### 2.1 Item 11 — every derived instrument load-bearing (discriminating form)

**Member used:** `.claude/skills/adr-write/SKILL.md` (PL-960 §6.2 member 5). Its H content is
the directory citation — the retired singular ADR directory → the current plural one, landed
at `71f5a22` (`/usr/bin/git show 71f5a22 -- .claude/skills/adr-write/SKILL.md`, two hunks: the
"File as..." line at the old line 22, and the README row at the old line 37).

**Procedure, in this worktree, restored afterward** (commands verbatim):
```
$ sed -i 's#File as `docs/adrs/NNNN-kebab-title.md`#File as `docs/adr/NNNN-kebab-title.md`#; \
    s#Then add the row to the table in `docs/adrs/README.md`.#Then add the row to the table in `docs/adr/README.md`.#' \
    .claude/skills/adr-write/SKILL.md
$ mkdir -p docs/adr
$ cat > docs/adr/ADR‑01064-test-instrument-revert-item-11.md   # the reverted instruction, followed literally
$ python3 scripts/audit-docs.py
$ rm -rf docs/adr && git checkout -- .claude/skills/adr-write/SKILL.md
$ git status --porcelain   # confirmed clean afterward
```
Step 1 reverted *only* the two directory-citation lines, leaving the citation rewrites
(`ADR-706`/`ADR-707`, `OQ-614`) in place. Step 2 produced the document the reverted
instruction mints, at the retired singular directory.

**Output (excerpt, the discriminating fire):**
```
FAILED (10):
  - check 5: ADR-1 referenced but no file exists
  - check 5: ADR-2 referenced but no file exists
  - check 5: ADR-3 referenced but no file exists
  - check 5: ADR-4 referenced but no file exists
  - check 5: ADR-5 referenced but no file exists
  - check 5: ADR‑1064 referenced but no file exists
  - check 31: docs/adr/ADR‑01064-test-instrument-revert-item-11.md: family 'decision' (prefix ADR) belongs under a 'adrs' directory, not 'adr'
  - check 36: .claude/skills/adr-write/SKILL.md:3: legacy adr path 'docs/adr/' (legacy pre-migration form survives)
  - check 36: .claude/skills/adr-write/SKILL.md:22: legacy adr path 'docs/adr/' (legacy pre-migration form survives)
  - check 36: .claude/skills/adr-write/SKILL.md:37: legacy adr path 'docs/adr/' (legacy pre-migration form survives)
EXIT=1
```

**Held.** Check 31 fires exactly on the document the reverted H content mints, naming the
wrong directory by name — the discriminating form PL-960:132-144 asks for. Check 36 also
catches the reverted H content itself as a legacy-form regression. **Verdict: EVIDENCED**, on
this one member. Not generalised to all thirteen members — item 12 (the W37-7 requirement-facing
proof) is the item that would.

### 2.2 Item 13 — vendored exemption reaches only the blanket passes

**Command, exactly as specified**, run from this worktree:
```
$ /usr/bin/git diff --stat 0651c1e 71f5a22 -- .claude/skills/brainstorming .claude/skills/code-quality \
  .claude/skills/create-adaptable-composable .claude/skills/dispatching-parallel-agents \
  .claude/skills/executing-plans .claude/skills/finishing-a-development-branch .claude/skills/graphify \
  .claude/skills/planning-with-files .claude/skills/receiving-code-review .claude/skills/reproducing-ci-locally \
  .claude/skills/requesting-code-review .claude/skills/secret-hygiene .claude/skills/security-audit \
  .claude/skills/subagent-driven-development .claude/skills/systematic-debugging .claude/skills/test-driven-development \
  .claude/skills/testing-strategy .claude/skills/ui-ux-pro-max .claude/skills/using-git-worktrees \
  .claude/skills/using-superpowers .claude/skills/verification-before-completion .claude/skills/vue-best-practices \
  .claude/skills/vue-debug-guides .claude/skills/vue-pinia-best-practices .claude/skills/vue-router-best-practices \
  .claude/skills/vue-testing-best-practices .claude/skills/writing-plans .claude/skills/writing-skills

 .claude/skills/planning-with-files/scripts/check-complete.ps1  |  2 +-
 .claude/skills/planning-with-files/scripts/set-active-plan.ps1 |  2 +-
 .claude/skills/requesting-code-review/SKILL.md                 |  3 +--
 .claude/skills/secret-hygiene/SKILL.md                         |  4 ++--
 .claude/skills/writing-plans/SKILL.md                          | 10 +++++-----
 5 files changed, 10 insertions(+), 11 deletions(-)
```

**Corrected reading (this checkpoint, after the deputy's review of an earlier draft of this
record).** RL-990 item 3 (`docs/rulings/RL-00990-...md:70-73`, quoted): *"A vendored skill's
own `SKILL.md` is stamped like the other 45 ... The files **beneath** it are exempt from
the blanket stamp, the tree-wide citation rewrite and check 37's shape check."* The tool
encodes the identical boundary at `scripts/doc-id.py:3870-3876`, `_is_vendored_exempt`:
*"exempt for a file beneath a vendored skill's boundary that is *not* the manifest itself
... The manifest ... is never exempt: it is stamped and its own citations rewrite like any
other file."* So `secret-hygiene/SKILL.md`, `writing-plans/SKILL.md` and
`requesting-code-review/SKILL.md` — themselves manifests — being stamped and having their
own citations rewritten (and, for `requesting-code-review`, a markdown reflow) **is by
design**, not a violation of item 13's clause; the population item 13 actually governs is
narrower: files **beneath** a manifest.

- **`.claude/skills/planning-with-files/scripts/check-complete.ps1` and
  `scripts/set-active-plan.ps1`** — both beneath `planning-with-files/SKILL.md`'s boundary
  — had PowerShell's scope-resolution operator (`::`) split into `: :` by the migration's
  sweep. A real violation: a file beneath a manifest is supposed to be untouched entirely.
  **FIXED BEFORE CLOSE by PR #788 → merged to `main` as `a8b3c39`** (deputy merge-ACK
  2026-09-18 01:43:02 BST) — restored byte-for-byte from `0651c1e` (== `fbb5555` for these
  two paths), sha256s in #788's own body.
- **The two named §5.4 content edits** — `writing-plans`'s own H content (line 19, the
  retired filename grammar, `` Save plans to: `docs/plans/YYYY-MM-DD-<feature-name>.md` ``,
  still present verbatim at `4d9fe1d`) and `subagent-driven-development`'s own H content
  (the `LG-` ledger-append routing; the file has zero diff `0651c1e`..`71f5a22` and its
  last touching commit is `ba76b3f`, #138, an old pre-migration commit) — **did not land**.
  These are edits the plan's own text (PL-960 §5.4, `:597-598`) requires as deliberate,
  named content changes to the manifests themselves, separate from the beneath-manifest
  exemption question. Their absence is a real violation of the plan's own clause.

**Verdict: item 13 HELD** for the files-beneath-a-manifest population — the two corrupted
scripts are **FIXED BEFORE CLOSE by PR #788 → main `a8b3c39`**; the three manifests' own citation
rewrites and reflow are by design and were never a violation. **The two named §5.4 content
edits did not land — REASSIGNED to W37-7** (PL-939 `:735`, the slice that applies the
conventions these two skills teach). **F111** (new, this checkpoint) — the mechanism gap
that let the sweep reach files beneath a manifest at all (the `::` split) — **owner
W37-11**, a `migrate()` change under the reproduction rule, not a content edit.

### 2.3 Item 14 — the three W37-4 deferrals

**Deferral 1** (RL-981, a fixture register row with no `decision:` must fail check 30):
the discharge mechanism the plan names — "§7.8 rewrites the register's header prose to
declare the row's field set... build the register-row check against that declaration" — is
**not check 30**. What exists is **check 29** (`check_register_grammar`,
`scripts/audit-docs.py:272`, `register-lint.py`'s `lint_register`), a separate check outside
the 30-39 family, because `docs/findings/register.md` is a markdown table and unreachable
from `_ID_SCOPE_ROOTS` (the plan's own stated reason). `uv run pytest -q tests/test_register_lint.py`
— **68 passed** (bare run: `68 passed in 0.42s`) — confirms check 29's own grammar tests are
green, but no test named or shaped like "a fixture row with no `decision:` fails check 30"
exists; the closest fixture tests (`test_a_bare_pipe_broken_row_is_refused`, and the
five-column-shape family) test a *different* defect class (a broken pipe / column count),
not a *missing* `decision:` field specifically.

**Deferral 2** (RL-989, "one predicate, not two" — `frozen_diff_is_permitted` reuse):
```
$ grep -n frozen_diff_is_permitted scripts/doc-id.py scripts/_docverify.py
(no output)
```
`frozen_diff_is_permitted` is defined and used only in `scripts/audit-docs.py` (`:2135`,
consumed by check 34's tests in `tests/test_audit_docs_ids.py`). `doc-id.py`'s row-(g)
frozen-family branch instead calls a **second, related but distinct** function,
`audit_docs.frozen_file_matches_after_migration_stamp` (`scripts/doc-id.py:10008`, itself
documented at `scripts/audit-docs.py:2265` as "(g)'s inverse" of `frozen_diff_is_permitted`).
So the two are related by design (one is the stated inverse of the other) but they are **two
predicates, not one reused** — RL-989's own acceptance item 3 (mutate check 34's DP-7
allowance and (g)'s frozen-family branch must change behaviour together) was not re-run this
record, and on the evidence above it cannot currently hold literally, since (g)'s branch does
not call the same symbol RL-989 named.

**Deferral 3** (check 36's canonical proof runs through the full ten-check orchestrator,
in-tree): no test matching this description — an in-tree `tmp_path`-free fixture restoring
orchestrator isolation for check 36's canonical proof — was found anywhere in
`tests/test_audit_docs_ids.py` or elsewhere in `tests/`. `grep -rn "orchestrator isolation\|reds only its target check" tests/`
returns nothing outside the plan's own text. The plan's own fallback applies: *"if it does not
[restore orchestrator isolation], re-defer with a named owner — silence is not one of
`CLAUDE.md` §13's four verdicts."*

**Verdict: DEFERRED WITH OWNER — lead / W37-11**, all three. None of the three plan-stated
discharge mechanisms is confirmed to exist as described; deferral 2's actual mechanism is a
related-but-distinct pair of functions rather than one reused predicate, and deferral 3's
fallback (re-defer with a named owner) is what applies here.

### 2.4 RFC-937 §7 (i) — every H row in §5 closed by a named commit

56 H / H+M rows sampled across §5.1-§5.5 and §5.8 (the concrete, individually-named rows;
large `M`-only aggregate rows such as `backend/src/app/` are out of (i)'s scope by
construction and excluded). Method: `/usr/bin/git log --oneline -1 -- <path>` per file, from
this worktree, against `main`'s reachable history.

| Row (§, file) | Last-touching commit | Verdict |
|---|---|---|
| `CLAUDE.md` | `71f5a22` | closed |
| `README.md` | `71f5a22` | closed |
| `.gitignore` | `71f5a22` | closed |
| `docs/README.md` | `71f5a22` | closed |
| `docs/roadmap.md` | `71f5a22` | closed |
| `docs/findings/register.md` | `71f5a22` | closed |
| `docs/findings/README.md` | `71f5a22` | closed |
| `docs/process/delivery-process.md` | `71f5a22` | closed |
| `docs/process/delivery-process.core.json` | `71f5a22` | closed |
| `docs/closures/README.md` | `71f5a22` | closed |
| `docs/rulings/README.md` | `71f5a22` | closed |
| `docs/ledgers/README.md` | `71f5a22` | closed |
| `docs/adrs/README.md` | `71f5a22` | closed |
| `docs/rfcs/README.md` | `71f5a22` | closed |
| `docs/plans/README.md` | `71f5a22` | closed |
| `docs/skills-map.md` | `71f5a22` | closed |
| `docs/workflows/README.md` | `71f5a22` | closed |
| `CONTRIBUTING.md` | `01ba0bd` (#495, pre-migration) | **NOT CLOSED — still pre-migration content** |
| `.github/PULL_REQUEST_TEMPLATE.md` | `01ba0bd` (#495, pre-migration) | **NOT CLOSED — still pre-migration content** |
| `docs/research/README.md` | — | **PATH DOES NOT EXIST** |
| `.claude/roles/auditor.md` | `71f5a22` | closed |
| `.claude/roles/decision-maker.md` | `71f5a22` | closed |
| `.claude/roles/executor.md` | `4d9fe1d` (#783, W37-6's own follow-up) | closed (within slice) |
| `.claude/roles/lead.md` | `4d9fe1d` (#783) | closed (within slice) |
| `.claude/roles/planner.md` | `71f5a22` | closed |
| `.claude/roles/reporter.md` | `71f5a22` | closed |
| `.claude/roles/watcher.md` | `71f5a22` | closed |
| `.claude/agents/README.md` | `71f5a22` | closed |
| `.claude/agents/ci-watcher.md` | `3f41d60` (#616, pre-migration) | **NOT CLOSED — still pre-migration content** |
| `.claude/agents/spec-reconciler.md` | `71f5a22` | closed |
| `.claude/skills/README.md` | `4d9fe1d` (#783) | closed (within slice) |
| `.claude/skills/writing-plans/SKILL.md` | `71f5a22` | closed (but see §2.2 — its own named H edit did not land) |
| `.claude/skills/subagent-driven-development/SKILL.md` | `ba76b3f` (#138, pre-migration) | **NOT CLOSED — still pre-migration content** (§2.2 confirms independently: zero diff 0651c1e..71f5a22) |
| `.claude/skills/close-workstream/SKILL.md` | `71f5a22` | closed |
| `.claude/skills/phase-review/SKILL.md` | `71f5a22` | closed |
| `.claude/skills/adr-write/SKILL.md` | `71f5a22` | closed |
| `.claude/skills/spec-change/SKILL.md` | `71f5a22` | closed |
| `.claude/skills/docs-audit/SKILL.md` | `71f5a22` | closed |
| `.claude/skills/dev-commands/SKILL.md` | `4d9fe1d` (#783) | closed (within slice) |
| `.claude/skills/git-hygiene/SKILL.md` | `71f5a22` | closed |
| `.claude/skills/reporter-cycle/SKILL.md` | `71f5a22` | closed |
| `.claude/skills/library-spike/SKILL.md` | `71f5a22` | closed |
| `.claude/skills/repo-architecture/SKILL.md` | `71f5a22` | closed |
| `.claude/skills/python-test/SKILL.md` | `4d9fe1d` (#783) | closed (within slice) |
| `.claude/skills/brainstorming/SKILL.md` | `7a50df3` (#76, pre-migration) | **NOT CLOSED — its own §5.4 one-sentence edit never landed** |
| `.claude/skills/planning-with-files/SKILL.md` | `95b1e24` (#79, pre-migration) | correctly excluded by design (RL-987/§6.3 — not a member; its row-mate `brainstorming` was the member, and see the row above) |
| `scripts/doc-id.py` | `71f5a22` | closed |
| `scripts/doc-index.py` | `71f5a22` | closed |
| `scripts/audit-docs.py` | `71f5a22` | closed |
| `scripts/register-lint.py` | `71f5a22` | closed |
| `scripts/register-owed.py` | `71f5a22` | closed |
| `scripts/req-coverage.py` | `71f5a22` | closed |
| `scripts/scope-audit.py` | `71f5a22` | closed |
| `scripts/file-census.py` | `71f5a22` | closed |
| `scripts/graphify-docs-extract.py` | `71f5a22` | closed |
| `.github/workflows/docs.yml` | `71f5a22` | closed |

**Summary: 49 of 56 closed within W37-6's own commit chain (`71f5a22`/`0651c1e`/`4d9fe1d`); 5
not closed (still carrying pre-migration content, contrary to RFC-937 §5's own H-row
listing); 1 path does not exist; 1 correctly excluded by design.**

**Verdict: REASSIGNED, per file** (the deputy's ruling on this record's earlier draft) —
**W37-11 owns the walk itself** (a fuller RFC-937 §7(i) sweep of all ~90 H/H+M rows), not
the individual files below, each reassigned to the slice whose leaf plan already owns that
area:

| File | Reassigned to | Basis |
|---|---|---|
| `CONTRIBUTING.md` | **W37-9** | PL-939 `:785`, root governance / public face |
| `.github/PULL_REQUEST_TEMPLATE.md` | **W37-9** | PL-939 `:785`, root governance / public face |
| `.claude/agents/ci-watcher.md` | **W37-8** | PL-939 `:760`, agents |
| `.claude/skills/writing-plans/SKILL.md` | **W37-7** | PL-939 `:735`, instruments — the same content-edit gap §2.2 already reassigns there |
| `.claude/skills/subagent-driven-development/SKILL.md` | **W37-7** | PL-939 `:735`, instruments — same basis |
| `docs/research/README.md` (1 missing path) | **W37-10** | PL-939 `:815`, docs READMEs |

`.claude/skills/brainstorming/SKILL.md` is not in the lead's named list above but carries
the identical class as `subagent-driven-development`'s gap (a named §5.4 one-sentence edit
that never landed on a vendored manifest — zero diff `0651c1e`..`71f5a22`, last touched by
`#76`, pre-migration): reassigned to **W37-7** on the same basis, stated rather than picked
silently, since no other slice's leaf plan claims it.

This is a sample (56 of the roughly 90 H / H+M rows RFC-937 §5 lists across the full
corpus, not every individually-named file under a large aggregate row); it is not (i)'s
exhaustive discharge — that fuller walk is W37-11's, not any of the reassigned slices'.

### 3. NFRs and enforcement (unchanged from the auditor's measurement)

Reproduced from auditor report §3, not independently re-measured a second time this record
except where §2 above already re-measured the same ground (item 11 = the "every derived
instrument load-bearing" row; item 13 = the vendored-exemption row):

| NFR / enforcement | Failing-case artifact | Verdict |
|---|---|---|
| CI verify's exit semantics 1/2/3 | CR-1063 §2: CI run `35261236904` on `323b523` exited 3 at `doc-id migrate --verify` (`--ref HEAD` resolved to the already-migrated PR merge ref); fix on record, post-fix CI on `f777159`/`main`@`71f5a22` green | evidenced — a real red run, cause and fix both on record |
| Row (g), broken down | CR-1063 §6: g1 (token-boundary/provenance/bare-comma) = 0/0/0 clean; g2 `classified-by-none` = 251 of 971, by cause (table in CR-1063 §3) | measured, not asserted |
| Every derived instrument load-bearing | §2.1 above | **evidenced this record**, on one member |
| Vendored exemption | §2.2 above | **did not hold this record**, on 5 files — deferred with owner |
| Scan-roots guard | `test_a_missing_notes_root_fails_the_audit` 1/1, on broken input | evidenced |
| `.venv/` sweep exclusion | `test_sweep_never_reaches_a_gitignored_path` + `test_sweep_still_reaches_an_untracked_unignored_path`, 2/2 | tests pass; mutation-proof (reverting the sweep to a bare walk) not run |
| Check 32 broken-input disposition | `test_audit_docs_check_32_disposition.py` 5/5 | evidenced |
| Fail-closed gate wrapper | not probed | **no failing-case proof found** |
| "migrate-over-a-venv refusal" | no literal refusal guard; mechanism is exclusion-by-construction (`git ls-files` enumeration never presents a gitignored venv as input) | no refusal to prove — the new `doc-id-migration-run` skill documents the hazard, not independently reproduced |

### 4. Scripts run this checkpoint, exact commands and exit codes

All at tree `a0dbd20a1b276028e9a84647fd17f2a28213627f` (this branch, `w37-6-checkpoint-3-close`,
rebased onto `origin/main` after PR #788 merged as `a8b3c39`, parent `29e7a9c` — `4d9fe1d` is
kept only where cited above as the auditor's own evidence tree):

```
$ python3 scripts/audit-docs.py; echo EXIT=$?
...
All checks passed.
EXIT=0

$ python3 scripts/doc-id.py check; echo EXIT=$?
EXIT=0

$ python3 scripts/doc-index.py --check; echo EXIT=$?
OK (byte-stable)
EXIT=0

$ uv run ruff check .
All checks passed!

$ uv run pytest -q tests/test_audit_docs*.py tests/test_doc_id.py -p no:cacheprovider
297 passed

$ uv run pytest -q tests/test_register_lint.py
68 passed in 0.42s

$ python3 scripts/register-owed.py W37-6
Generated by `python3 scripts/register-owed.py W37-6` against `a0dbd20 ("w37-6-checkpoint-3-close")`.
21 owed row(s), 2 matched but excluded as opening with a resolution marker.

$ python3 scripts/register-owed.py W37-11
Generated by `python3 scripts/register-owed.py W37-11` against `a0dbd20 ("w37-6-checkpoint-3-close")`.
7 owed row(s), 0 matched but excluded.

$ uv run python scripts/req-coverage.py
requirements specified : 533
requirements marked    : 338  (63.4%)
(repo-wide, unrelated to this slice — unchanged from the auditor's own measurement)
```

### 5. What was not delivered

- **Row (g)** — standing, disclosed FAIL (§1b item 7, §3). Not this record's to fix; owner
  W37-11, `#757` first item.
- **The idempotence gap, PL-960:909** — a second `migrate` run over already-migrated output,
  zero diff, was not proven; only first-run determinism was. Filed as register finding **F107**
  (new, this checkpoint), owner W37-11, with CR-1063 §5's numbers.
- **Check 35's two-clause output shape** — fires on one non-markdown file after F87's
  widening; an output-shape question, not fixed here. Filed as register finding **F108** (new,
  this checkpoint), owner lead, decaying to W37-11.
- **The pinned-base CI-verify read** (CR-1063 §3) — `.github/workflows/docs.yml:117` and
  `_docverify.py:4333` (`load_w37_11_record(snap.control)`) read the W37-11 record from the
  pinned control tree forever, so a post-migration record edit on `main` is invisible to the
  standing CI verify. Filed as register finding **F109** (new, this checkpoint, added on the
  lead's extension to the brief after review 13's recommendation), owner lead/W37-11; the
  two-option decision (control tree vs. live tree) is not made here — it is a row for
  W37-11's own leaf plan `Decision points` table, not a silent pick.
- **The `(d → W37-11)` docstring/implementation mismatch** (CR-1063 §4) —
  `_h1_residue_by_file`'s docstring (`scripts/_docverify.py:3054-3056`) and `tracked_files`'s
  docstring (`:428-430`) disagree about which population a sweep-excluded file's per-file
  attribution reaches. Filed as register finding **F110** (new, this checkpoint), owner
  lead/W37-11 — disclosed only, not fixed.
- **Item 13's vendored exemption** — held for the files-beneath-a-manifest population; the
  two corrupted `.ps1` scripts are FIXED BEFORE CLOSE by PR #788 → main `a8b3c39` (§2.2);
  the two named §5.4 content edits (`writing-plans`'s filename grammar,
  `subagent-driven-development`'s `LG-` routing) did not land — reassigned to W37-7; the
  sweep-reaches-vendored mechanism gap filed as F111, owner W37-11.
- **Item 14's three W37-4 deferrals** — none of the three stated discharge mechanisms is
  confirmed as described (§2.3). Deferred with owner, lead/W37-11.
- **RFC-937 §7(i)** — 6 of 56 sampled H rows not closed plus 1 missing path, each
  reassigned per file to W37-7/8/9/10 (§2.4's table); W37-11 owns the fuller (i) walk
  itself, not the individual files.
- **21 owed register rows** (`register-owed.py W37-6`, auditor report §2/§4) — by disposition:
  F87 discharged this checkpoint (§ register update); F90 no-change (CR-1050); F92
  reconciled this checkpoint (owner W37-11, count corrected); F103, F105, F106 carry forward
  with owner (W37-6 lead); F80-F82, F88 limb 2, F89, F94-F97, F99-F102 as the auditor report
  §4 states (not started / carry forward unowned / accept, per finding).
- **Full local pnpm suite, mypy, `generate-contracts.py --check`** — this is **no longer
  an open gap**: the lead's own full local gate ran on `03e1cb0` (tree == `ce808d7`, this
  PR's base) at 2026-09-18 01:26:49, `handover/gate-03e1cb0/gate.log`: 13/13, `3436 passed,
  3 skipped, 1 xfailed` (collected 3440 == ran 3440). This record's own local run (§4)
  covers `audit-docs.py`, `doc-id.py check`, `doc-index.py --check`, `ruff`, and the two
  named pytest targets, on this record's own head — not a second full gate run, since the
  base tree's is already evidenced.

### 6. Roadmap and ledger

`docs/roadmap.md:766`'s WK-697 row is rewritten in this same PR, per `PL-939:863`
("the roadmap row (the lead's to apply; not written by this plan)") — drafted by the executor
here, for the lead's review before the PR leaves draft; it now also cites this record
(`CR-1065`) as checkpoint-3's own close record. `docs/plans/PL-01058-w37-6-migration-run-ledger.md`
carries this checkpoint's ledger entry and the dated correction to `:37-38`, in the same PR.

**Fix-before-close, separate PR:** PR #788 restored `.claude/skills/planning-with-files`'s
two `.ps1` scripts to their upstream bytes (§2.2) — merged to `main` as `a8b3c39` (deputy
merge-ACK 2026-09-18 01:43:02 BST), CI green (`docs` run `35292264867`, `history-policy`
run `35292264778`); this PR is rebased onto it.

## 7. Verdict

**Slice closes on a clean audit and the lead's merge (`CLAUDE.md` §13); the maintainer-line
question of `PL-1058:37-38` is ruled by the deputy** — recorded here per the deputy's ruling
of 2026-09-18 00:55:09 BST (`to-lead.md`, quoted in §0 above): checkpoint 3 does **not** gate
on a maintainer-dated acceptance line; that line belongs to review 13 (`CR-1064`, pending)
and to the
Work close (W37-11). Checkpoint 3 is met by (1) this record's clean checklist and the lead's
four verdicts, with every delivered-but-untested item re-measured (§2: item 11 held; item 13
held for the files-beneath-a-manifest population, the two corrupted scripts FIXED BEFORE
CLOSE by PR #788 → main `a8b3c39`, with the two named §5.4 content edits reassigned to
W37-7 and the mechanism gap filed as F111 for W37-11; item 14 not holding, deferred with
owner; RFC-937 §7(i) partially
held, its gaps reassigned per file to W37-7/8/9/10, the fuller walk owned by W37-11); (2) this PR, gated and CI green,
merged under the deputy's merge-ACK; (3) review 13 (`CR-1064`, PR #786, merged `ce808d7`)
already filed as a proposal with its acceptance line pending, and the pending acceptance
lines on reviews 12 and 13 reported to the maintainer as open and binding nothing.

**This record makes no close disposition of its own** — per `CLAUDE.md` §13 a Slice closes on
a clean audit and the lead's merge, neither of which this record performs. The lead's merge of
this PR, under the deputy's merge-ACK, is checkpoint 3's own close event.

**Ledger "ruled met" line:** pending the deputy's entry after this PR merges (see
`docs/plans/PL-01058-w37-6-migration-run-ledger.md`'s checkpoint-3 entry, filed alongside this
record).

## 8. Correction — 2026-09-18 (lead's verdict, filed in the channel at 09:53:03 BST)

**This record is write-once and merged; nothing above is edited.** This section is appended,
in the same annotated-in-place form `PL-1058:37-38` uses: the omitted scope item is named,
the words that framed the scope and the verdict are quoted as originally written, and the
correction follows with its own date and authority.

**The omission.** §1 above reads, quoted in full and unchanged: *"Scope is derived from
`docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`, Slice W37-6 (`:667-733`);
`docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md`'s 14-item Acceptance Standard
(`:71-162`); and RFC-937 (`docs/rfcs/RFC-00937-...md`) §7 (a)-(i)."* `PL-939:690-691` — inside
that very `:667-733` range, Slice W37-6's own "What lands in this one commit" — reads:

```
…the process-core digest; the roadmap restructure into milestone sections with
`WK-`/`SL-` rows; and `delivery-process.md`'s §3 vocabulary.
```

and `PL-939:907-908`, the map plan's self-review "Spec coverage" mapping, reads:

```
**Spec coverage.** Every §5 sub-section maps to a slice: §5.1 → W37-9; §5.2 → W37-6 (M rows,
the roadmap restructure, the process vocabulary) and W37-10 (H rows); §5.3 → W37-8; §5.4 →
```

So the roadmap restructure, `SL-` rows included, is **W37-6's own declared deliverable, named
twice** — inside the scope range §1 cites — and neither §1a's precondition table nor §1b's
14-item/RFC-937 §7 table, both drawn from `PL-960`'s Acceptance Standard and RFC-937 §7 (a)-(i)
rather than from the map plan's own slice section, gives it a verdict. Measured at
`d63f765085fe6eb1c594177c5779ecfc3caf7ae8`: `docs/roadmap.md` has **5** `## P` milestone
sections (P1a:188, P1b:386, P2:551, P3:844, P4:986), **41** `### WK-` rows with `### WK-697`
at :754, and **0** `### SL-` rows. This record itself mentions none of it
(`grep -icE 'roadmap restructure|milestone section|SL-'` against this file at that tree → `0`).

**The verdict.** The milestone-section and `WK-`-row half of the roadmap restructure is
**DELIVERED at `71f5a22`**. The `SL-` row half is **REASSIGNED from W37-6 to W37-10, dated
2026-09-18** — W37-10 owns `docs/roadmap.md`'s H rows (`PL-939:908`) and its filed leaf plan
already carries the row-cutting task; **W37-11 verifies at the Work close**. This is expressly
**not** the claim that the gap predates W37.

**Amendment to §7's "Verdict."** §7 above is not withdrawn: its "clean audit" reading **stands
for everything the checklist actually examined** — the 6 preconditions, the 14-item/RFC-937 §7
table, and the re-measures in §2. It did not examine the map plan's own slice-section prose
outside that table, which is where the omitted deliverable was named. The checklist's
disposition on every item it did examine is unchanged by this correction.

**The cause.** The scope table at §1 was built from `PL-960`'s 14-item Acceptance Standard and
RFC-937 §7 (a)-(i) — neither names the roadmap restructure — rather than from the map plan's
own Slice W37-6 section (`PL-939:667-733`) directly, even though §1 cites that very range as
part of scope. `CLAUDE.md` §13 requires: *"Scope is derived from the specification first, then
evidenced — never from recollection of what was built. Reversed, an audit is silent about what
is missing."* (`CLAUDE.md:255-256` at `origin/main` `d63f765`.) The scope table's route through
the leaf plan's own acceptance list, rather than through the map plan's slice prose directly,
is that reversal, and this omission is its consequence.

Full evidence, register row and finding: `docs/findings/register.md` (`F112`) and
[`FD-1074-no-sl-row-exists-for-any-slice-and-no-plan-carries-slice.md`](../findings/FD-01074-no-sl-row-exists-for-any-slice-and-no-plan-carries-slice.md).

## §8 — Second dated correction, 2026-09-19: deliverables asserted in `PL-960` prose

**Why this append exists.** `PL-960` asserts, in several places, that a deliverable *"is in this
commit"*. One such claim was checked during W37-7 and found false at the tree. A sweep of the class
found five more claims of the same shape. **W37-6's close gave none of them a verdict**, and
`CLAUDE.md` §13 permits four verdicts of which silence is not one.

**The mechanism, and it is the second instance of one cause.** The close's scope table was derived
from the plan's *"what lands"* list at `:691`, while these deliverables live in **sentences inside
§6 and §7 table cells**. A scope derived from one list cannot see a deliverable asserted in prose
elsewhere in the same document. **The first instance was the `SL-` rows** (this record's first
dated correction). This is the second.

### The six claims, each with its verdict

| Line | Claim | Verdict |
|---|---|---|
| `:648` | the `close-workstream` half of §5.4's bespoke-audit rule *"is in this commit, where the rule is authored"* | **Delivered late.** `bespoke` measured 0 in `close-workstream/SKILL.md`, 0 in `docs-audit/SKILL.md` and 0 in this record, at `3803331`. Delivered by W37-7 Task 9 at `11ea5c0`: authored in full in `close-workstream` (`:609`), with `docs-audit` carrying its reading-instrument half at `:398` and a **pointer** at `:404`, not a second copy. Verified by W37-11 at the Work close |
| `:620` | *"Every charter's **M** row — the mechanical citation rewrite — lands in this commit regardless"* | **Delivered in part; residue deferred with owner W37-8, gated on the maintainer's charter line.** See the proxy note below |
| `:634` | *"Either way both are in this commit, so the risk is closed"* | **Not started.** See below |
| `:693` | *"15 are already in this commit for another reason: all 13 `docs/_templates/` files and `document-ids.md` … and `delivery-process.md`"* | **Delivered.** `docs/_templates/` holds exactly 13 tracked files; both named paths present at `3803331` |
| `:892` | the `REFERENCE.md` vendored-detection comment corrected, *"Violation: the template still names `LICENSE` presence as the decider after this commit"* | **Delivered.** Deciding sentence at `REFERENCE.md:45-52`: *"Which skills count is a hand-kept list, not a filesystem property … RL-990 rejected that detection rule."* The rejected wording is gone; `git grep` for it under `docs/_templates` returns nothing |
| `:1034` | *"Two of the nine are §6.2 members … so they are in this commit for two independent reasons"*, inside §7.10's checklist | **Delivered in part; residue not started, owner W37-7, verified by W37-11.** `_VENDORED_SKILLS` and the ruff-exclude reconciliation landed (`scripts/_docid.py:982`, `:1072`). **Zero** `SKILL.md` files carry `vendored: true` or `origin:` — no skill carries any stamp — and `.claude/skills/README.md` has no class-covering-28 deviation record |

### `:634` — why a count could not settle it

The claim is a disjunction: if `close-workstream` carries the `FD-` essay's **header and shape** as
well as the register row's, `auditor.md`'s adoption is belt-and-braces; if not, `auditor.md` carries
that instruction alone — *"Either way both are in this commit, so the risk is closed."*

Measured at `3803331`: `close-workstream/SKILL.md` has 0 `FD-`, 0 "essay", 7 "register row";
`auditor.md` has 0 `FD-`, 1 "essay", 2 "register row". **The second limb obtains**, which the plan
permits only if `auditor.md` carries the instruction alone.

**A keyword count reports "essay: 1 hit" and settles nothing**, so the text was read whole by a
named reader. `auditor.md:33-35`:

```text
Evidence essays live at `docs/audit/findings/<F-id>.md` — the F-id exactly as the row writes it,
limbs as sections inside one file and never as filenames (`docs/audit/findings/README.md` has the
rules and the migration constraints).
```

That is **a filename-and-location instruction plus a pointer**. It is silent on the essay's header
and on its shape, and `FD-` never appears. **So the limb the plan relies on does not hold, and the
sentence declaring the risk closed is not supported at this tree.**

### `:620` — the proxy that passed it and the predicate that failed it

**This row records its own measurement failure, because that is its value.**

The claim was first checked with `grep -c 'docs/notes'` across the charters, which returned **0
everywhere** and was read as "the rewrite landed". That predicate is **blind to the pre-migration
audit path** — the literal is in the exhibit above, not spelled here, because this record is
subject to the same check it is describing. Re-measured at `3803331` with the real predicate:

| Charter | `docs/notes` (proxy) | `audit path` (predicate) |
|---|---|---|
| `auditor.md` | 0 | **3** |
| `planner.md` | 0 | **2** |
| the other five | 0 | 0 |

**Five pre-migration path sites survive in two charters.** The residue is `:620`'s, not a separate
finding: the same claim, unfinished.

**Owner W37-8** (charters). Its charter edits are gated on the maintainer's dated line, so the
verdict is **deferred with owner W37-8, gated on that line**.

### New row — the audit scope is narrower than the migration's write set

**Why did no check fire on five pre-migration paths in files the migration itself wrote?**
`audit-docs.py`'s own header states checks 30–39 are *"path-scoped to `_ID_SCOPE_ROOTS` until the
migration (Slice W37-6) widens it to the whole corpus"*, and `.claude/` is outside that scope.
`71f5a22` touched **58 files under `.claude/`**.

**So the instrument is structurally incapable of catching the migration's own misses in the largest
directory it wrote.** This is the audit-scope disclosure carried unfiled since W37-6, now with its
measured instance. **Owner W37-11.**

### New row — `task-brief`'s dangling plan paths

`task-brief`'s header comment cited two plan paths by their **pre-migration dated filenames**, both
measuring `MISSING`, while `.claude/skills/README.md`'s entry for that same script already carried
the **migrated** names. **The manifest was updated and the file beneath it was not.** That is
`CR-1065:199-202`'s mechanism as a **live instance** rather than a described risk, which is stronger
evidence for that row than its description. Fixed under W37-7 Task 11 Step 3; the row is
**W37-11's**.

### New row — the plan template's `Verified` step does not fit vendored skills

Across W37-7 Tasks 6, 7, 10 and 11 — four vendored skills — the per-task *"refresh `Verified`"* step
was **inapplicable every time**: none has a `Verified` section, and none of their README rows sits
in a table with a date column. Each was recorded inapplicable with its reason rather than satisfied
by an unrecorded edit to a vendored manifest, which `CLAUDE.md:214` forbids.

**The template assumes a repo-local skill shape.** For the vendored population §12's mechanism is
the README deviation record instead. **Not four coincidences — a template defect. Owner W37-10**,
which owns `docs/` and `docs/_templates/`.

### New row — the near-miss, recorded because the lesson is the reviewer's

While verifying `:648`, the executor read `PL-960:648` through `cut -c1-200`, saw the row **without
the quoted claim**, and concluded `PL-1070` had cited the wrong line. It had not: the quote is the
**tail** of that same long row. **It was one message from filing a false finding against a correct
citation**, and the only thing that caught it was re-reading the whole line before writing the
report.

In its words: **"a fragment read gets an invented frame, and a truncating pipe is a fragment read
that does not announce itself."** The lead and the deputy both read plan rows through `cut`
throughout the same session.

### Proxy-predicate failures in this work, stated because the finding is about exactly this

Five, across three people, while measuring findings about instruments that answer confidently and
answer a different question:

1. An intersection counting ids present in two files, when the question was ids naming two different
   things.
2. A delimiter-anchored pattern blind to CSV-quoted fields, undercounting a block by the seven rows
   whose titles needed escaping.
3. A `join` on a numerically sorted set returning **a confident zero** — no error, no warning, the
   most reassuring answer available — caught only because a reader refused to believe an absence.
4. A count of quote-bearing lines used as a count of entries; it happened to agree.
5. `grep -c 'docs/notes'` as a proxy for "the citation rewrite landed", blind to the
   pre-migration audit path. **The only one of the five that reached a verdict.**

**A seventh instance, produced by this very record.** Naming the pre-migration audit path as this
append's own subject matter turned check 36 red at five sites, all inside the appended text. The
check cannot distinguish a path named **in order to record that it moved** from one left behind.
The remedy taken was **a fenced exhibit plus descriptive prose**, never a ceiling row: raising a
pooled ceiling to silence a record about pooled ceilings would be the defect performing itself.
