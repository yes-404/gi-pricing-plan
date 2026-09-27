---
id: LG-1143
family: ledger
title: W37-9 — root governance, CLAUDE.md and the public face
status: closed
created: 2026-09-27
owner: executor
tree: 823a75efb5da70d8c652c91fd6dc54e5ab966149
phase: P2
work: WK-697
plans: [PL-1072]
corrected_by: []
relates: []
---

# LG-1143 — W37-9 — root governance, CLAUDE.md and the public face

Executed task by task from `PL-1072` (`status: active`, frozen 2026-09-27), under
`RL-1142` (DP-1 (c), DP-2 (b), DP-3 (b), DP-4 (a), DP-5 (a)). Cut from `origin/main` at
`823a75efb5da70d8c652c91fd6dc54e5ab966149` (#816, RL-1142 + PL-1072 activation). **One
PR, one branch (`w37-9-root-governance`)**, per the plan's own Task 9 and the lead's
09:02:53 BST addendum — so every task commit below is pre-squash by construction:
**cited as "pre-squash branch commit of this PR, reachable via `refs/pull/817/head`"**,
never as a squash SHA. This PR's own squash SHA on `main` is recorded once, in the
closing record, the same convention `LG-1141` uses for its final PR.

## Tasks

### Task 1 — `CLAUDE.md` §2 and §4, the layout tree and module map

Fixed the mangled `WF-698…05` range to the five ids individually (`WF-698`…`WF-702`);
added `docs/INDEX.md` and `docs/process/document-ids.md` pointers to §4; added one
sentence to §2 naming `document-ids.md` §1.4 as the `docs/` layout authority. Dated
amendment (F49's CI enforcement) kept verbatim. `python3 scripts/audit-docs.py` →
`EXIT=0`.

Landed in: this PR — pre-squash branch commit `bbd6c567`, reachable via
`refs/pull/817/head`.

### Task 2 — `CLAUDE.md` §5 and the §0 bullet, G2's permanence yield

Both permanence sites (`:27`, `:117`) edited in one commit, each with a dated line
naming RFC-937 D2. DP-1 (c) applied: the third "permanent" hit (§12) left unedited as a
citation of §5. **Corrected in a second commit**, per the deputy's review: both stamps
renamed to name the amending authority — "Amended 2026-09-27 by the maintainer (dated
line by delegation, D3), on RFC-937 D2" — since an amendment to what `CLAUDE.md`
requires is the maintainer's (§12), here by delegation.

Landed in: this PR — pre-squash branch commits `bd5d367b` (both sites) and `67e2e8a3`
(authority-wording correction), reachable via `refs/pull/817/head`.

### Task 3 — `CLAUDE.md` §9, §12 and §13–§15, the pointers

§9 names a phase's rows as `WK-`/`SL-` families (no counts or status added). §12 points
at `document-ids.md` §1.6, the roles-per-family owner table. §13 gains record-destination
pointers (`CR-` `docs/closures/`, `FD-` `docs/findings/` + `register.md`, `RL-`
`docs/rulings/`, `LG-` `docs/ledgers/`); the F85 predicate clause and §14's RFC-711
citation kept unchanged. §15's own mangled `WF-698…05` token (found while auditing Task
1) fixed to the five ids. `python3 scripts/audit-docs.py` → `EXIT=0`; all four
`grep -c` counts (`docs/closures/`, `docs/findings/`, `docs/rulings/`,
`document-ids.md`) `>= 1`.

Landed in: this PR — pre-squash branch commit `3b284d8f`, reachable via
`refs/pull/817/head`.

### Task 4 — `README.md`, the tour and how things are named

DP-5 (a): the closure-record link repointed from the legacy audit directory to
`docs/closures/`. Added the "how things are named" paragraph pointing at
`document-ids.md`; the DP-3 (b) branch/PR-title convention with its dated
not-yet-in-force clause; three new Explore bullets (`docs/plans/`, `docs/rulings/`,
`docs/closures/`).

Landed in: this PR — pre-squash branch commit `e312373c`, reachable via
`refs/pull/817/head`.

### Task 5 — `CONTRIBUTING.md`, ids, and where the work lives

DP-5 (a): register link repointed to `docs/findings/register.md`. Added where findings
(`FD-`), proposals (`RFC-`) and rulings (`RL-`) go, keeping the "issues are intake,
register is truth" framing. Added `doc-id.py next` and the id/family rule. Added the
DP-3 (b) branch/PR-title convention, word-for-word with `README.md` up to the
not-yet-in-force clause, with the triage-mint / maintenance-item / bot-exemption detail
`README.md` points here for.

Landed in: this PR — pre-squash branch commit `a7e0bd3f`, reachable via
`refs/pull/817/head`.

### Task 6 — `.github/PULL_REQUEST_TEMPLATE.md`, the required slice line

`NT-` token removed. Added the required `SL-`/`PL-` line with DP-3 (b)'s dated clause,
the triage mint, the standing `WK-` maintenance item, and the bot-author exemption — all
four clauses present. `## Scope` and `## Evidence` unchanged.

Landed in: this PR — pre-squash branch commit `f7f2552b`, reachable via
`refs/pull/817/head`.

### Task 7 — `.gitignore` and the issue templates

`.gitignore`'s family sentence reworded (`PL-` `docs/plans/`, `LG-` `docs/ledgers/`,
`RL-` `docs/rulings/`, `RFC-` `docs/rfcs/`), replacing the retired-notes-directory form;
reasoning sentences (unaudited-account argument, leading-slash anchoring note)
kept verbatim. Added DP-2 (b)'s optional `related` id field to both issue templates;
example ids (`FR-451`, `ADR-703`, `FD-894` — the plan's own example did not resolve,
substituted) verified live. Parsed with `PyYAML` in this worktree's `.venv` (a parser
*is* available here, correcting this plan's own G4 assumption): both templates parse
clean, `bug.yml` body ids `[None, 'version', 'reproduction', 'expected', 'observed',
'context', 'related']`, `question.yml` body ids `['category', 'body', 'related']`.

Landed in: this PR — pre-squash branch commit `a318b280`, reachable via
`refs/pull/817/head`.

### Task 8 — the three `M` rows, verify only

No edit; all three verify clean.

- `SECURITY.md:40` links `docs/process/security-posture.md`; the file exists.
- `.importlinter` (DP-4, fact confirmed unmoved): `grep -n '^name'` → `ADR-703`,
  `ADR-704`, `DEP-3`; both ADR files present under `docs/adrs/`; `uv run lint-imports` →
  `Contracts: 3 kept, 0 broken`, `EXIT=0`.
- `pyproject.toml` + `packages/*/pyproject.toml`: 3 `ADR-` ids (703, 704, 707) and 13
  distinct `FR-` ids cited in comments; every one resolves (`ADR-` under `docs/adrs/`,
  `FR-` bold-defined in `docs/specs/`). No `NFR-` cited, no unresolvable id.

No commit — evidence recorded here and in the PR body's disposition table.

### Task 9 — this ledger, the full gate, the disposition table, the PR

This file. The §2b mitigation re-run (`FD-1066`…`FD-1069`, all filed, all owned by
`W37-11`, none naming a §5.1 file this slice owns). `docs/INDEX.md` regenerated,
byte-stable (`doc-index.py --check` → `EXIT=0`). The full two-half gate is recorded
below: it ran at `11e3cc2b`, a pre-squash branch commit of this PR, reachable via
`refs/pull/817/head`. The final head differs from it only in this ledger. *(Corrected
2026-09-27 by the auditor, at slice close, finding F-a of pass (a): this paragraph first
said the gate ran at "this PR's final head", which it did not.)*

Landed in: this PR — the ledger and gate-evidence commits, reachable via
`refs/pull/817/head`; the PR's own squash SHA on `main` is recorded once, in the
closing record.

## PRs

| # | Branch | Squash SHA on `main` | Tasks | State |
|---|---|---|---|---|
| #817 | `w37-9-root-governance` | `49c06ad7fb9f1bccf648abb270c0b6df81d386cf` | 1–9 | merged 2026-09-27 10:18:45 BST |

## Gate evidence

Full two-half gate at head `11e3cc2b73288a4617682e45caf3d737f2da3ea0`, a pre-squash
branch commit of this PR, reachable via `refs/pull/817/head`. Evidence is in
`~/gi-pricing-plan.local/handover/gate-11e3cc2/` (local, not repo); `HEAD.txt` was
written before the run.
`uv run pytest --collect-only -q` → 3462 tests collected (matches `main`).

Python/docs half, 7/7 `exit=0`: ruff, mypy, import_linter, audit_docs, req_coverage,
contracts, pytest (`3458 passed, 3 skipped, 1 xfailed`). `audit-docs.py` → `EXIT=0`,
`All checks passed.`, `DISCLOSED (865, at or under the W37-11 residue ceiling)`.

Frontend half, 6/6 `exit=0`: install, generate:api, lint, type-check, test (`97 files /
602 tests passed`, `Type Errors: no errors`, exit code read directly), build.

**An earlier run at head `e3542f83`** (a pre-squash branch commit of this PR, reachable
via `refs/pull/817/head`) **genuinely failed** (`audit_docs`/`pytest`, 2 of 7) on
two real defects this executor introduced in the first cut of this file — a padded id
outside a link target (twice, `LG-1141`/`FD-894` written padded) and one dead example id
that did not resolve, plus one literal retired-path spelling. Fixed in `11e3cc2b`;
the corrected head is the one gated above. Full PR body has the per-`.rc` table.

**Final-head delta.** From `11e3cc2b` to the PR's final head `e46d3b18` (a pre-squash
branch commit of this PR, reachable via `refs/pull/817/head`), the diff is this ledger
only (+25/−11). That delta is carried by
`~/gi-pricing-plan.local/handover/gate-e46d3b1/` (local, not repo; `HEAD.txt` =
`e46d3b18`): `tests/` `1020 passed, 1 skipped`, rc 0; `audit-docs.py` rc 0,
`All checks passed.`, `DISCLOSED (865, at or under the W37-11 residue ceiling)`;
`doc-id.py check` rc 0; `doc-index.py --check` rc 0, `OK (byte-stable)`. The
`CLAUDE.md` blob is `c7f4773f` at both heads, so the deputy's D3 dated line of
2026-09-27 09:56:38 BST carries to the final head.

## Slice close — the auditor's record

**Status set `closed` by the auditor on 2026-09-27** (`document-ids.md` §1.6, SL row:
*"auditor closes: sets the `LG-` `closed`, verifies acceptance"*). The lead ruled at
2026-09-27 10:19 BST (as amended at 10:20 BST) that the close lands in one post-merge,
docs-only PR authored by the auditor, built on `LG-1141`'s closing record and touching
exactly two paths: this file and `docs/INDEX.md`. W37-9 closes when this PR merges. A
Slice closes on a clean audit and the lead's merge, with no maintainer line (`CLAUDE.md`
§12, §13).

**The work PR, #817.** It was squash-merged onto `main` as the SHA in the PRs table above,
on 2026-09-27 at 10:18:45 BST. Its parent is `823a75ef`, the cut base, and its PR head was
`e46d3b18`, a pre-squash branch commit of this PR, reachable via `refs/pull/817/head`. The
deputy's MERGE ACK for #817 is 2026-09-27 10:18:13 BST, in
`~/gi-pricing-plan.local/channel/to-lead.md` (local, not repo). The deputy's D3 dated
line is 09:56:38 BST, in the same file.

**Pass (a), the audit of #817 before the merge.** The auditor proposed findings, and the
lead adopted them as verdicts:
- at `e46d3b18`: CLEAN, with the minor findings F-a and F-b (lead's verdict, 2026-09-27
  10:17:39 BST, in `~/gi-pricing-plan.local/channel/to-deputy.md`).

Pass (a)'s results:
- the two-way match between the nine §5.1 rows and this ledger has no gaps and no extras;
- the SHA sweep found MAIN 1, BRANCH 10 commits, NEITHER 0;
- acceptance items 2–10 and 12 were re-run at the final head, and all passed.

**Findings, with owner and resolution:**

| Finding | Raised | What | Owner | Resolution |
|---|---|---|---|---|
| F-a | pass (a), at `e46d3b18` | Task 9 said the gate ran at "this PR's final head", but it ran at `11e3cc2b`. The gate section cited `11e3cc2b` and `e3542f83` without the pre-squash marking. | auditor | **Fixed in this closing record.** Task 9 and the gate section now say the full gate ran at `11e3cc2b`, and the final-head delta is ledger-only, carried by `gate-e46d3b1`. `11e3cc2b`, `e3542f83` and `e46d3b18` are each marked as a pre-squash branch commit of this PR, reachable via `refs/pull/817/head`. |
| F-b | pass (a), at `e46d3b18` | The PR body's disposition table used its own row numbers, not §5.1's. It also cited DP-1's third site at the line it had at `bd5d367b`, not at the final head. | lead | **Fixed by the lead in #817's body before the squash** (2026-09-27 10:15 BST). |

**Pass (b), the reachability sweep after the merge — run by the auditor, re-stamped
2026-09-27 10:22:34 BST.**
- **Tree:** the squash commit's tree equals `e46d3b18`'s tree, `44c8470b`, so the §5.1
  content is on `main` byte for byte.
- **Predicate, verbatim:** `git show <squash>:docs/ledgers/LG-01143-w37-9-root-governance-claude-md-and-the-public-face.md | grep -oE '\b[0-9a-f]{7,40}\b' | sort -u`.
  Each token is checked with `git merge-base --is-ancestor <t> <squash>` (exit 0 gives
  MAIN), and otherwise with the same check against `e46d3b18` (exit 0 gives BRANCH).
- **MAIN ×1:** `823a75ef`.
- **BRANCH ×12 tokens (10 commits), 0 NEITHER:** `bbd6c567`, `bd5d367b`, `3b284d8f`,
  `67e2e8a3`, `e312373c`, `a7e0bd3f`, `f7f2552b`, `a318b280`, `e3542f83`, and `11e3cc2b`,
  which the ledger spells three ways. All are pre-squash branch commits of #817, reachable
  via `refs/pull/817/head`.

**Tokens this section adds, which pass (b) did not cover, are swept here** with the same
predicate:
- `823a75ef` and the squash SHA: MAIN;
- `e46d3b18`: BRANCH, via `refs/pull/817/head`;
- the tree id `44c8470b`: NOTCOMMIT.

**Final-head delta:** recorded in "Gate evidence" above (F-a).

**Acceptance, verified by the auditor** (`PL-1072` Acceptance Standard):

| Item | Result | Where evidenced |
|---|---|---|
| 1 | Pass. Covered by items 2, 3, 7, 10 and 11. | below |
| 2 | Pass. The maintainer's line is given by delegation: D3, 09:56:38 BST. The `CLAUDE.md` blob is `c7f4773f` at both `11e3cc2b` and `e46d3b18`. | re-run at `e46d3b18` |
| 3 | Pass. The dated RFC-937 lines are adjacent to the §0 bullet and §5's rule, and `grep -c RFC-937 CLAUDE.md` is 3. §12's mention is left as a citation (DP-1 (c)). | re-run at `e46d3b18` |
| 4 | Pass. The four `grep -c` counts are 1, 2, 1 and 7. | re-run at `e46d3b18` |
| 5 | Pass. The fenced dead-path sweep over eight files prints nothing, exit 1. | re-run at `e46d3b18` |
| 6 | Pass. `WF-698` to `WF-702` each resolve under `docs/workflows/`. | re-run at `e46d3b18` |
| 7–9 | Pass. `audit-docs.py`, `doc-id.py check` and `doc-index.py --check` each give rc 0. `INDEX.md` is byte-stable after a fresh regeneration. | re-run at `e46d3b18` |
| 10 | Pass. `lint-imports` shows 3 contracts kept, 0 broken. | re-run at `e46d3b18` |
| 11 | Pass. The two-half gate is 13 × rc 0 at `11e3cc2b`; the final-head delta is carried by `gate-e46d3b1`. CI at `e46d3b18` is all success: docs 36307857511, python 36307857488, history-policy 36307857569. | "Gate evidence" |
| 12 | Pass. `git diff --name-only 823a75ef...e46d3b18 -- docs/specs/` is empty. | re-run |
| 13 | Pass. All nine §5.1 rows are dispositioned, none silent. The body's numbering was corrected before the squash (F-b). | #817 body |
| 14 | Pass. The deputy's ACK is at 10:18:13 BST and the lead's CLEAN verdict at 10:17:39 BST. The two-way match and ancestry are recorded under pass (a) and pass (b) above. | above |

**Residue carried, not fixed here:** none.
