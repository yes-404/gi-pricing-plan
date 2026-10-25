---
id: RS-1891
family: research
kind: audit
title: FD-1887 fix slice SL-1888 (WK-1178) delta audit 59759536 to b781ec96, B1 and B2 of RS-1890 landed
status: draft
created: 2026-10-25   # drafted 2026-10-25 under working id 8234; minted 2026-10-25 as RS-1891
owner: auditor
tree: b245c193ce1013d07bfe4541472055cc41d87f3e
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-1888, LG-1889, RS-1890, FD-1887]
---

# RS-1891 — FD-1887 fix slice SL-1888, delta audit 59759536 → b781ec96

*(Working id 8234, written by `aud-8194d`, 2026-10-25, from `brief-aud-8194d-2026-10-25.md` (lead 28), docs only, no heavy check run. Check 31/32 on this id and on FD-1887, SL-1888, LG-1889, RS-1890 are expected until the mint. Proposes; the lead adopts.)*

## Question

Authority: `to-lead.md` "2026-10-25 19:07:02 GMT" (a), as the brief quotes it: "one docs-only sonnet auditor seat per slice … scope = own docs delta audited head → gate head, the patch-id equality quoted, AND verification that RS 8213's and RS 8214's B1/B2 are landed as dated LG lines (that closes the NOT-CLEAN)". Does the slice's own change from the audited head `59759536` (RS-1890) to the gate head `b781ec96` stay in scope, and are B1 and B2 landed?

## Method

Read-only, in `.claude/worktrees/aud-8194d` at `b781ec96` (`origin/main` `ef3ac6c8`). `git diff`, `git show`, `git grep`. Own-delta paths = `git diff --name-only 59759536 b781ec96 -- docs` minus `git diff --name-only <mb(59759536)> <mb(b781ec96)> -- docs` (paths main changed in the window; merge-bases `4e399fd0` and `01a28e6d`). No audit-docs, pytest or build was run (owed, below).

## Checks

1. **Non-docs patch-id equality.** Predicate: `git diff $(git merge-base <h> origin/main) <h> -- . ':!docs' | git patch-id --stable`.
   - `59759536` (merge-base `4e399fd0`): `b947186dcc1c757b025b7e1cd0e0460d5ce76fec`.
   - `b781ec96` (merge-base `01a28e6d`): `b947186dcc1c757b025b7e1cd0e0460d5ce76fec`.
   - **Equal.** The only non-docs path is `tests/test_fremtpl2_data_guard.py`; the guard is code-identical to the audited head.
2. **The slice's own docs delta.** Commits in `59759536..b781ec96` that are the slice's own: `520f8968` (LG), `0197a8bd` (FD essay, register row, RS-1890), `c95ca7fd` (INDEX), and the merge `b781ec96` (brings main `01a28e6d`). Against the merge-base `01a28e6d`, the slice's docs diff is six paths (+276 lines, no deletions).

   | Path | Change | Verdict |
   |---|---|---|
   | `docs/ledgers/LG-1889-…-slice-ledger.md` | +36 lines (`520f8968`): section "Corrections after the slice audit" (lines 90–124), B1 table and B2 limits | IN SCOPE; it is the B1/B2 answer, see check 3 |
   | `docs/findings/FD-1887-….md` | new, 67 lines (`0197a8bd`); `status: active`, working id; Remedy carries H1/H2 as a second step "owed before the P2 close, owner WK-1178" | IN SCOPE; the fold the lead's 12:02:21 entry ordered |
   | `docs/findings/register.md` | +1 row (FD-1887) | IN SCOPE; the auditor's own register row |
   | `docs/research/RS-1890-….md` | new, 60 lines (`0197a8bd`); front matter `status: draft` | IN SCOPE; the audit being folded, per common brief item 34 |
   | `docs/INDEX.md` | +4 rows: FD-1887, SL-1888, LG-1889, RS-1890 (`c95ca7fd`) | IN SCOPE; regenerated, see INDEX `--check` below |
   | `docs/roadmap.md` | +20 lines: the SL-1888 row (from `7529198e`, before the audited head; merged with main's own roadmap edits) | IN SCOPE; unchanged slice row, status `active` |

   Paths in the window changed by main alone (`docs/contracts/…`, FD-1713/1850/1872 essays, other LGs and RSs, `docs/specs/02-modelling.md`, `03-rating-engine.md`) are not the slice's and are not judged.
3. **B1 and B2 of RS-1890.** RS-1890 asked for LG wording. Quoted from `RS-1890-…` lines 53–54:
   - **B1:** "Correct LG-1889's two statements of Check 7: say the three `71e481fa-*` logs name their head only in the file name and carry no `rc=` line, with the exit codes inferred from the summary, or add the head and rc lines to the logs."
   - **B2:** "Add Check 3's found shapes to the LG's stated limits, or drop "cannot miss" from any PR text; the LG's wording today ("Its limits, stated: …") lists two of the seven."

   | Item | Landed text in LG-1889 on `b781ec96` | Verdict |
   |---|---|---|
   | B1 | Line 90: "## Corrections after the slice audit (appended 2026-10-23 12:00 BST, head `59759536`)"; line 94 "### B1 — what each log actually carries"; line 96: the statement "the log's first line the head it ran on" "is **false for the three `71e481fa-*` logs**: their first line is a `run-small: waiting …` line and the sha is in the file name only"; table at lines 98–105 (line 1, last line, `rc=` line, head inside); line 107: "(a) `rc=1`, (b) `rc=0`, the guarded variant `rc=0`, and (e) `rc=0` … the exit code is inferred from [the pytest summary]". Table agrees with RS-1890 check 7 (three `71e481fa-*` logs: no `rc=`, no head; `b0d2580c…` and `c-proof.log`: both). | **LANDED** (dated 2026-10-23 12:00 BST; line 90) |
   | B2 | Line 109 "### B2 — the guard's stated limits (replaces "a static guard that cannot miss")"; "The slice does not claim a guard that cannot miss; that claim is withdrawn"; "Caught" list; "Missed" list of five shape groups (lowercase `fremtpl2` parts-built path, renamed or string-fetched reader, subprocess reader, conftest or other-file helper, unrelated guard counted); "No live miss is shown at `59759536`"; line 124: H1 and H2 named as a maintainer decision. | **LANDED** (same dated block) |

   The original Build-log lines above line 90 are unchanged; the block says "where they disagree with this block, this block governs" (line 92). That follows the append-only rule and is why B1 reads as landed rather than rewritten.
4. **RS 8214.** The brief's authority text names "RS 8214's B1/B2". `ls docs/research | grep 8214` is empty, and `git grep -nE "RS[ -]8214" b781ec96 -- docs` finds nothing. **Not present on this branch; not audited.** If RS 8214 is another seat's record on another branch, its B1/B2 need their own check; this record covers RS-1890 only.
5. **One observation, not a B-item.** LG line 124 says "If the limits above are accepted as recorded, neither [H1 nor H2] needs a slice". The FD-1887 essay (Remedy, second step) records the later ruling `to-lead.md` "2026-10-23 12:02:21 BST" (2): H1 and H2 are "hardening owed before the P2 close, owner WK-1178". The two do not conflict in what the slice does (the LG's block is dated 12:00, before the ruling, and the essay is the register of the owed work), but a reader of the LG alone misses the owed step. The lead may add one dated LG line pointing at the essay; no verdict depends on it.
6. **Reachability of evidence.** `git merge-base --is-ancestor 520f8968 b781ec96` rc 0. The ledger SHAs RS-1890 checked (`d66ad2ed`, `b0d2580c`, `ca2057fb`, `7529198e`, `71e481fa`) were found reachable at `59759536`; `59759536` is an ancestor of `b781ec96` by the range above.

## Owed (not run, docs-only seat, no grant)

audit-docs, register-lint, req-coverage, generate-contracts `--check`, the eight docs-audit pytest files (common brief item 30). They belong to the docs-only gate and the mint.

## Proposed verdict (the lead's to adopt)

**CLEAN.** The non-docs patch-id is equal at both heads (`b947186d…`), every slice-own docs change is in scope, and RS-1890's B1 and B2 are LANDED as a dated LG block (line 90). The NOT-CLEAN of RS-1890 closes on this evidence for the RS-1890 items. Open for the lead: RS 8214 was not found (check 4); the LG-versus-FD pointer (check 5, optional).
