---
id: CR-1065
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: W37-6 (WK-697 slice 6) — checkpoint 3 close
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-18
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: 4d9fe1d62328285ac0483b047c3959e39e0f5bd6
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
acceptance lines on reviews 9-13 are reported to the maintainer as open and binding nothing
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
| 8 (h) Full gate green | (h) | `audit-docs.py`/`req-coverage.py` clean; CI green on `71f5a22` (4 runs); mypy/pytest/pnpm not re-run this session | **EVIDENCED** — gate 13/13 on `f777159` (tree == `71f5a22`'s), `handover/gate-f777159/gate.log`, + main CI ×4 on `71f5a22` (run ids `35268549712`/`35268549550`/`35268549539`/`35268549620`) | Local re-run this checkpoint: `python3 scripts/audit-docs.py` exit 0, `uv run pytest -q tests/test_audit_docs*.py tests/test_doc_id.py` — see §4 |
| 9 Scan-roots guard re-derived | — | `test_a_missing_notes_root_fails_the_audit` 1/1; 5-path mutation not re-run | **EVIDENCED** (fresh run) | as above |
| 10 Widened scope = stamped set | — | check 30: 446/66 F83 skips, not cross-checked against §4 step 5 set | **EVIDENCED** (fresh run) | as above |
| 11 Every derived instrument load-bearing | — | not re-run by either session | **re-measured before the cut** | **RE-MEASURED, HELD.** See §2.1 — fires exactly as the discriminating form requires |
| 12 Requirement-facing proof (W37-7) | — | W37-7 not started | **not started — W37-7's, not W37-6's** | unchanged |
| 13 Vendored exemption reaches only blanket passes | — | not re-run | **re-measured before the cut** | **RE-MEASURED, DID NOT HOLD.** See §2.2 — moved to **deferred with owner, lead/W37-11** |
| 14 Three W37-4 deferrals discharged | — | not independently re-confirmed | **re-measured before the cut** | **RE-MEASURED, PARTIALLY HELD.** See §2.3 — one confirmed by symbol, one discharge-mechanism mismatch found, one no in-tree fixture test found; moved to **deferred with owner, lead/W37-11** |
| (i) Every H row in §5 closed by a named commit | (i) | not walked row-by-row | **re-measured before the cut** | **RE-MEASURED, PARTIALLY HELD.** See §2.4 — 56 H/H+M rows sampled; 49 closed within W37-6's own commit chain, 5 not closed (still carrying pre-migration content), 1 path does not exist, 1 correctly excluded by design. Moved to **deferred with owner, lead/W37-11** for the 5 gaps + 1 missing path |

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

**Did not hold.** Expected: byte-identical except `writing-plans` and
`subagent-driven-development` differing by their own named §5.4 edits. Actual:

- **`subagent-driven-development` has *zero* diff** — its own named §5.4 H edit (the `LG-`
  ledger-append routing) never landed. Independently confirmed by
  `/usr/bin/git log --oneline -1 -- .claude/skills/subagent-driven-development/SKILL.md` →
  `ba76b3f` (#138), an old, pre-migration commit — the file has not been touched since.
- **`writing-plans`'s diff is not the expected §5.4 edit.** Its own named H content — line 19,
  `` Save plans to: `docs/plans/YYYY-MM-DD-<feature-name>.md` `` (the retired filename
  grammar) — is **still present verbatim at `4d9fe1d`** (read directly). What actually
  changed is citation rewrites (three pre-migration reference tokens rewritten to their `RFC-895`/`WK-671`/`RL-906` post-migration forms) —
  ordinary M-step mechanical rewrites, which item 13's own rule says a vendored file should
  not receive at all.
- **`planning-with-files`'s two `.ps1` scripts are corrupted**, not edited: `[Console]::Out`
  → `[Console]: :Out` and `[System.IO.File]::WriteAllText` → `[System.IO.File]: :WriteAllText`
  — a `::` (PowerShell scope-resolution operator) split into `: :` by the sweep. Not a
  citation rewrite of any kind; a defect in the migration's own text-rewrite pass reaching
  into a vendored subtree it should never touch.
- **`requesting-code-review/SKILL.md`** and **`secret-hygiene/SKILL.md`** were also touched —
  the former by a markdown line-join (`[Subagent returns]:\n  Strengths:` →
  `[Subagent returns]: Strengths:`), the latter by citation rewrites (two pre-migration
  reference tokens rewritten to their `RFC-842`/`WK-670` post-migration forms). Neither is a "blanket pass" (header stamp only) and neither is one of the
  two named §5.4 edits.

**Verdict: DEFERRED WITH OWNER — lead / W37-11.** Five vendored files carry unauthorised
content changes (two corrupted, three receiving M-step rewrites the rule forbids), and one
named §5.4 edit (`subagent-driven-development`) never landed while the other
(`writing-plans`) landed as the wrong edit. This is a real gap in RL-990's acceptance items
2-4, not a re-confirmation of them.

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

**Verdict: DEFERRED WITH OWNER — lead / W37-11**, for the 5 not-closed rows
(`CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.claude/agents/ci-watcher.md`,
`.claude/skills/subagent-driven-development/SKILL.md`, `.claude/skills/brainstorming/SKILL.md`)
and the 1 missing path (`docs/research/README.md`). This is a sample (56 of the roughly 90 H
/ H+M rows RFC-937 §5 lists across the full corpus, not every individually-named file under a
large aggregate row); it is not (i)'s exhaustive discharge, and is reported as such.

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

All at tree `4d9fe1d62328285ac0483b047c3959e39e0f5bd6` (this worktree, branch
`w37-6-checkpoint-3-close`), after §2's reverts:

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
(see PR body / commit for the pass count — no failures)

$ uv run pytest -q tests/test_register_lint.py
68 passed in 0.42s
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
- **Item 13's vendored exemption** — did not hold; 5 files carry unauthorised content
  (§2.2). Deferred with owner, lead/W37-11.
- **Item 14's three W37-4 deferrals** — none of the three stated discharge mechanisms is
  confirmed as described (§2.3). Deferred with owner, lead/W37-11.
- **RFC-937 §7(i)** — 5 of 56 sampled H rows not closed, 1 path missing (§2.4). Deferred with
  owner, lead/W37-11.
- **21 owed register rows** (`register-owed.py W37-6`, auditor report §2/§4) — by disposition:
  F87 discharged this checkpoint (§ register update); F90 no-change (CR-1050); F92
  reconciled this checkpoint (owner W37-11, count corrected); F103, F105, F106 carry forward
  with owner (W37-6 lead); F80-F82, F88 limb 2, F89, F94-F97, F99-F102 as the auditor report
  §4 states (not started / carry forward unowned / accept, per finding).
- **Full local pnpm suite, mypy, `generate-contracts.py --check`** — not run this checkpoint
  either (the auditor report's own residual gap, §2); this record's own local run (§4) covers
  `audit-docs.py`, `doc-id.py check`, `doc-index.py --check`, `ruff`, and the two named pytest
  targets, per this checkpoint's own required checks.

### 6. Roadmap and ledger

`docs/roadmap.md:766`'s WK-697 row is rewritten in this same PR, per `PL-939:863`
("the roadmap row (the lead's to apply; not written by this plan)") — drafted by the executor
here, for the lead's review before the PR leaves draft. `docs/plans/PL-01058-w37-6-migration-run-ledger.md`
carries this checkpoint's ledger entry and the dated correction to `:37-38`, in the same PR.

## 7. Verdict

**Slice closes on a clean audit and the lead's merge (`CLAUDE.md` §13); the maintainer-line
question of `PL-1058:37-38` is ruled by the deputy** — recorded here per the deputy's ruling
of 2026-09-18 00:55:09 BST (`to-lead.md`, quoted in §0 above): checkpoint 3 does **not** gate
on a maintainer-dated acceptance line; that line belongs to review 13 (`CR-1064`, pending)
and to the
Work close (W37-11). Checkpoint 3 is met by (1) this record's clean checklist and the lead's
four verdicts, with every delivered-but-untested item re-measured (§2, with two of four
re-measures — items 13 and 14 — not holding and moved to deferred-with-owner, and RFC-937 §7
(i) partially held, also moved to deferred-with-owner); (2) this PR, gated and CI green,
merged under the deputy's merge-ACK; (3) review 13 (`CR-1064`, PR #786, merged `ce808d7`)
already filed as a proposal with its acceptance line pending, and the pending acceptance
lines on reviews 9-13 reported to the maintainer as open and binding nothing.

**This record makes no close disposition of its own** — per `CLAUDE.md` §13 a Slice closes on
a clean audit and the lead's merge, neither of which this record performs. The lead's merge of
this PR, under the deputy's merge-ACK, is checkpoint 3's own close event.

**Ledger "ruled met" line:** pending the deputy's entry after this PR merges (see
`docs/plans/PL-01058-w37-6-migration-run-ledger.md`'s checkpoint-3 entry, filed alongside this
record).
