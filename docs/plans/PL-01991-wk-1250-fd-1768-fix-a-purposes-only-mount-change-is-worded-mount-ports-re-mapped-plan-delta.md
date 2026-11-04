---
id: PL-1991
family: plan
kind: map
title: WK-1250 — FD-1768's fix, a sub-graph mount whose purposes alone changed is worded "mount ports re-mapped" in the declared changes (FR-1399), SL-1989 — a dated Work-plan delta
status: active                  # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-03             # filed under working id 8298
owner: planner
tree: a8ef6f19c0be1142b0ac9dea88086f1ce6f95cbe
phase: P2
work: WK-1250
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1254, FD-1768, RL-1686, RL-1344, FR-1399]
---

(Minted 2026-11-04 from working id 8298, with SL-1989 from working id 8296 and LG-1990 from working id 8297, on the lead's mint order and the maintainer's GO "2026-11-03 17:30:53 GMT", with the mint tool of record `mint-repoint.py` (sha256 `4d83681a`); finding FD-1768; executed on branch `sl-8296-wk1250-fd1768-purposes-wording`.) The blockquote below is the plan's draft-time wording and keeps the working ids.)

2026-11-04 — activated by its slice's PR (L1), to-lead 2026-11-04 01:30:18 GMT ruling (a).

# PL-1991 — WK-1250: FD-1768's fix. A purposes-only mount change is worded "mount ports re-mapped" (SL-1989, a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"): a new `PL-` that `relates:` the Work's plan, `PL-1254`,
> and leaves it unedited. It holds one slice row, SL 8296, with ledger LG 8297. The executor's
> skills are `superpowers:test-driven-development` and `.claude/skills/python-test`. Add
> `.claude/skills/spec-change` if DP-7 is ruled (a). PL 8298, SL 8296 and LG 8297 are working
> ids, written in space form in prose until the mint.

## Authority

- **The owed fix.** The register row `docs/findings/register.md:392` reads (FD-1768, MEDIUM,
  owner WK-1250): "**fix before close with an owner: WK-1250**, a follow-up slice after SL-1341
  merges (the `before == after` branch words ports and purposes separately, with a test
  changing `purposes` alone). The event that next discharges it: the merge of that slice."
  SL-1341 is `closed` (`docs/roadmap.md`, its row under `### WK-1250`).
- **The seating.** The maintainer's entry "2026-11-03 15:58:45 GMT" item (1) in
  `~/gi-pricing-plan.local/channel/to-lead.md`: "a dated WK-1250 delta row, SL-1989 / LG-1990,
  red-first …, merge target Fri 6, GO request to me with the row".
- **The form.** The lead ruled option (a) on 2026-11-03: a new delta PL under working id 8298,
  as `PL-1667` and `PL-1737` are, with `PL-1254` unedited.
  *(Added 2026-11-03 by the planner (seat plan-fd1768b, lead 30), on the lead's ruling (a) in
  `~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`, entry "2026-11-03 16:00:22 GMT",
  which stands on `.claude/roles/planner.md` "Lean P2" L1 (a'). This plan replaces the "row 4"
  that was appended to `PL-1254` on `draft/pl-fd1768` at `03085614`. That append is reverted by
  `28ef6c4f` on the same branch, so `PL-1254` is unedited. Its content is carried here unchanged
  in substance: SL-1989 / LG-1990, R0 (as Evidence), R1, R2, G, A1 to A8, and DP-5 to DP-7 with
  their recommendations. The DP numbers are the row's.)*
- **The calendar.**
  - The entry "2026-11-03 15:38:58 GMT" sets the code freeze on Tue 10 Nov 2026, the docs freeze
    on Wed 11 Nov 2026 and the P2 exit demo on Wed 18 Nov 2026.
  - The entry "2026-11-03 15:59:27 GMT" says nfr-bench-1 runs on a dedicated VM and "do[es] not
    reserve the shared box's gate slots". The same entry says "The fresh full gate at the
    post-FD-1768 head runs on the shared box as soon as SL-1989 merges — Fri 6 evening …; Mon 9
    is the fallback, not the plan".
  - Weekdays were read with `date -d <d> +%A`.

## Goal

When only the `purposes` selector of a sub-graph mount changes, the declared change says that
the purposes changed. It must not say "ports re-mapped". Every description that `RL-1686` rules
for the other mount changes stays the same, character for character. The merge discharges
FD-1768.

## Evidence at `a8ef6f19` (read, not run)

- **The structural diff is correct, and this corrects a misreading.** The interim of the
  WK-1250 close auditor (aud-wk1250), as the lead relayed it and as the entry of 15:58:45 repeats
  it, says that `rating.py:1093-1095` "emits before==after for a purposes-only change" as part of
  the defect. That part is not a defect.
  - `packages/model-schema/src/model_schema/rating.py:1093-1095` (`_diff_mounts`) keeps a mount
    whose `ref` is the same on both sides when `ports_changed` or `purposes_changed` is true.
  - So a `purposes`-only change becomes one `AlgorithmSubGraphChange` with `before == after`,
    `ports_changed=False` and `purposes_changed=True` (the model is at `:950-965`).
  - That is what `RL-1344` acceptance 5 requires: "A change to a mount's `purposes` alone
    appears in FR-219's structural diff" (`RL-1344` :197-198).
  - **`model-schema` is not changed by this slice, so `docs/contracts/` does not regenerate.**
- **The defect is the wording, in `pricing-core` only.**
  - `packages/pricing-core/src/pricing_core/rating/analysis.py:662-664` reads
    `elif mount.before == mount.after:` and then
    `text = f"{point}: mount ports re-mapped ({mount.after})"`. It reads neither `ports_changed`
    nor `purposes_changed`.
  - The re-point branch (`:665-669`) adds `; ports re-mapped` when `ports_changed` is true. It
    says nothing when `purposes_changed` is true (DP-6).
- **The strings are ruled.**
  - `RL-1686` "Descriptions" (`:261-267`) fixes the exact forms: `<mount_point>: mount added
    (<after>)`, `<mount_point>: mount removed (<before>)`, the re-point form `<mount_point>: mount
    <before> → <after>`, the re-map suffix `; ports re-mapped`, and the re-map alone
    `<mount_point>: mount ports re-mapped (<ref>)`.
  - It has no form for a `purposes` change, so a new form needs a ruling (DP-5).
- **The tests.**
  - `packages/pricing-core/tests/test_rating_attribution.py:1356-1384`
    (`test_mount_ports_re_mapped_forms`, marked `req("FR-1399")`) asserts the two forms that name
    ports.
  - No test in that file changes `purposes`.
  - The backend's change summary already words both flags:
    `backend/src/app/platform/change_summary.py:144-145` has `(ports changed)` and
    `(purposes changed)`.
- **The requirement.**
  - `docs/specs/03-rating-engine.md:198`, FR-1399, has the mount sentence of its clause
    *(Amended 2026-10-14, WK-673, RL-1686, `FD-1660`.)*: "Each mount the structural diff (FR-219)
    reports as added, removed, re-pointed or re-mapped is exactly one derived change".
  - A change to `purposes` alone is none of those four (DP-7). FR-219 (`03`:88) does not name
    mounts.
- **The CI path filters.**
  - `.github/workflows/python.yml` fires on `packages/**`, and `docs.yml` fires on `docs/**`.
  - `frontend.yml` fires only on `frontend/**`, `docs/contracts/openapi/**`,
    `packages/pricing-core/src/pricing_core/modelling/**` and its own file. `analysis.py` is under
    `pricing_core/rating/`, so it is not in that set.
- **No database.** The test file and the two files it imports from
  (`test_rating_dislocation.py`, `test_rating_score.py`) have no `DATABASE_URL`, no `conftest_db`
  and no DB fixture. The predicate was `grep -ln "DATABASE_URL\|conftest_db"`, and it gave no
  hit.

## Decision points

These are for the decision-maker. The GO request carries them to the maintainer. Each one is
resolved by a ruling before the slice starts.

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-5 | What is the exact description of a mount change whose `ref` did not move? | (a) Keep `RL-1686`'s forms and add purposes in the same suffix form. Ports alone: `<mp>: mount ports re-mapped (<ref>)`, unchanged. Purposes alone: `<mp>: mount purposes changed (<ref>)`. Both: `<mp>: mount ports re-mapped (<ref>); purposes changed`. (b) Name the selectors: `<mp>: mount purposes <old> → <new> (<ref>)`, with a word for an absent selector (all purposes). (c) Use one neutral form, `<mp>: mount changed (<ref>)`, plus the suffixes. | **(a).** Every ruled string and the existing test stay the same. It uses the vocabulary the backend change summary already uses ("purposes changed", `change_summary.py:145`). It needs no rule for rendering an absent selector. (b) gives more detail, but it needs its own rule for `None`. (c) changes the ruled ports-only string that `test_mount_ports_re_mapped_forms` asserts. |
| DP-6 | Is the re-point branch in scope? There `ref` moves and `purposes` changes too, and the description says nothing about purposes (`analysis.py:665-669`). FD-1768's disposition names only the `before == after` branch. | (a) In scope: add `; purposes changed` after `; ports re-mapped`, with one more test case. (b) Out of scope: file it as a separate finding. | **(a).** It is the same loop and the same test. The text leaves out a change but does not misstate one. (b) would add a record for about two lines of code. |
| DP-7 | FR-1399's mount sentence lists "added, removed, re-pointed or re-mapped" (`03`:198). A `purposes`-only change is a derived change in the code, but the sentence does not name it. | (a) A dated amendment to FR-1399 in this slice, in the same commit as the code: "… re-pointed, re-mapped, or with its `purposes` selector changed …". (b) No spec edit, because `RL-1344` acceptance 5 already rules that the diff carries the change. | **(a).** The spec is the contract that the code is written against (`CLAUDE.md` §2). Without (a), FR-1399 says nothing about a change that the code derives and that A3 asserts. The cost is one sentence and one `req-coverage` run. |

## Acceptance Standard

Each item is checked by a command that a fresh reviewer can run from the repository root on the
slice's merge tree. Items 1 and 2 apply to this plan. Items A1 to A8 apply to the slice.

1. **This delta passes the docs checks on its own branch.** At the branch head,
   `python3 scripts/audit-docs.py` prints no line that names this file, except the lines of
   checks 31 and 32 for the working ids. Those are expected until the mint. After the mint,
   `python3 scripts/audit-docs.py` and `python3 scripts/doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>`
   prints no line that stands for a set of ids.

The slice, SL-1989:

- **A1.** `git diff --name-only origin/main...HEAD` lists only these paths:
  `packages/pricing-core/src/pricing_core/rating/analysis.py`,
  `packages/pricing-core/tests/test_rating_attribution.py`, the `LG-` under `docs/ledgers/`,
  `docs/INDEX.md`, `docs/roadmap.md` (the SL row), this plan (its `status:` only), the FD-1768
  essay and `docs/findings/register.md` (A8), and `docs/specs/03-rating-engine.md` if DP-7 is
  (a). It lists nothing under `packages/model-schema/`, `docs/contracts/`, `backend/` or
  `frontend/`.
- **A2.** The `LG-` holds R1's red line, run at the base. The line shows the failing assert and
  the actual string, `mount ports re-mapped`.
- **A3.** `test_mount_purposes_changed_forms` passes at the head. Its description assert is
  DP-5's ruled string, character for character.
- **A4.** `test_mount_ports_re_mapped_forms` passes unedited:
  `git diff origin/main...HEAD -- packages/pricing-core/tests/test_rating_attribution.py` shows
  added lines only.
- **A5.** `git grep -n "mount ports re-mapped" -- packages` shows the one f-string in
  `analysis.py`, which runs only when `ports_changed` is true, and the existing test lines.
- **A6.** The GREEN set is found by import closure (the common seat brief, item 29). The `LG-`
  quotes the commands and the list.
- **A7.** The full code gate, both halves, is green at the re-merged head, and every rc is
  quoted. `generate-contracts.py --check` is rc 0. If DP-7 is (a), `req-coverage.py` is rc 0.
- **A8. FD-1768's closing act.** The auditor sets FD-1768 `status: closed` and marks the register
  row :392 resolved, citing the PR number and the merge commit by sha. This is the event that the
  row names: "the merge of that slice". The act goes with the slice's mint and closing acts.
  `docs/INDEX.md` is regenerated after it (the common seat brief, item 17).

## Global Constraints

- **The money and the price are untouched.** The change is to wording only (FD-1768: "no pricing
  effect"). No step, pin, hash or allocation path changes.
- **Nobody hand-writes a shape that is in `model-schema`** (`CLAUDE.md` §2), and
  `docs/contracts/` is generated and never edited by hand. This slice touches neither. A change
  under either one stops the slice.
- **A requirement id is permanent** (`CLAUDE.md` §5). DP-7 (a) adds a dated clause, never a
  new id.
- **Red first, and red by its cause** (`superpowers:test-driven-development`). A fixture or
  compile error is not the red.
- **No test is removed or weakened** (the common seat brief, item 13).

## Tasks

### SL-1989 — FD-1768's fix: a purposes-only mount change is worded "mount ports re-mapped"

**The row.** Order 1 in this delta, and the fourth slice of WK-1250 after `PL-1254`'s Slices 1
to 3. Ledger LG-1990.

- **Scope:** R1, R2 and G below.
- **Requirement:** FR-1399 (`03` §3).
- **Register:** FD-1768 (MEDIUM, owner WK-1250) closes at the merge (A8).
- **Depends on:** SL-1341 (closed), DP-5 to DP-7 ruled, and the maintainer's GO on this row.
- **Size:** 1, with one `sonnet` executor.
- **Merge:** by **Fri 6 Nov 2026**, and earlier if it is ready ("earlier is never blocked",
  the entry "2026-11-03 15:46:13 GMT"). The fresh WK-1250 full gate runs at the post-merge head the
  same evening (the lead's, per the entry of 15:59:27). **Mon 9 Nov 2026 is the fallback**, and
  the code freeze is **Tue 10 Nov 2026**.

**R1 — red first, on main, with no database.**

1. Add `test_mount_purposes_changed_forms`, marked `req("FR-1399")`, to
   `packages/pricing-core/tests/test_rating_attribution.py`.
2. Build it from the file's own helpers: `_e_mounted`, `_mounted_base`, `_mounted_version`,
   `_candidate_version`, `_resolver` and `_mount_changes`.
3. The candidate changes only the `m_ncd` mount's `purposes`, for example from absent to
   `["mid_term_adjustment"]` (`MountPurpose`,
   `packages/model-schema/src/model_schema/scoring.py:57`).
4. Assert that there is exactly one derived mount change, that its kind is `step_changed`, and
   that its description is DP-5's ruled form.
5. If DP-6 is (a), add a second case that changes `ref` and `purposes` together. It asserts the
   re-point form followed by DP-5's suffix.
6. Run the test through `~/gi-pricing-plan.local/handover/run-small.sh` as one file with
   `-k test_mount_purposes_changed_forms`.

**The red, by its cause:** an `AssertionError` on the description, whose actual string is
`m_ncd: mount ports re-mapped (sub_graph:ncd-ladder@4)`. The `LG-` quotes the assert line and
the actual string.

**R2 — green.**

- In the mount loop of `analysis.py`, the `before == after` branch words each flag that is true,
  in DP-5's ruled form. Ports alone keeps today's string exactly.
- If DP-6 is (a), the re-point branch adds the purposes suffix after `; ports re-mapped`.
- Nothing else in `analysis.py` changes.
- If DP-7 is (a), FR-1399's mount sentence gets its dated amendment in the same commit as the
  code (`.claude/skills/spec-change`).

**G — the gate.**

- The diff leaves `docs/` (`packages/pricing-core/**`), so the full code gate runs, with both
  halves (`CLAUDE.md` §11; the common seat brief, item 30). The slice runs it in a gate slot.
  nfr-bench-1 is on its own VM (the entry of 15:59:27), so the gate does not wait for it.
- The CI that fires, from the path filters: `python.yml`, `docs.yml` and `history-policy.yml`.
  `frontend.yml` does not fire.
- There is no contract regeneration.

### Write set

- `packages/pricing-core/src/pricing_core/rating/analysis.py`: the mount loop only
  (`:650-676`).
- `packages/pricing-core/tests/test_rating_attribution.py`: one added test.
- LG-1990 under `docs/ledgers/`.
- `docs/specs/03-rating-engine.md`: FR-1399, only if DP-7 is (a).
- At the mint: the SL-1989 row under `### WK-1250` in `docs/roadmap.md`, `docs/INDEX.md`, the
  `status:` of this plan, and the FD-1768 closing act (A8).

## Hand-off (not this plan's writes)

- The rulings on DP-5 to DP-7 belong to the decision-maker.
- The maintainer's GO on the row comes before the executor is briefed.
- The SL-1989 roadmap row and the mint belong to the lead.
- The `LG-` belongs to the executor.
- FD-1768's closing act belongs to the auditor.
- The post-merge WK-1250 full gate belongs to the lead.
- `PL-1254` is not edited.

## Self-review

1. **Every cite was read.** Every `file:line` above was read at `a8ef6f19`. The channel entries
   were read from `to-lead.md`.
2. **Every requirement is named by id.** The only one is FR-1399, and no range is used.
3. **No placeholders.** The one exception is DP-5's ruled string, which A3 reads from the ruling.
4. **The misreading is corrected in the text.** The Evidence section says that `rating.py` is
   correct and that the defect is in `analysis.py:662-664` only.
5. **The calendar is stated once and agrees with the channel.** The merge is Fri 6, the fallback
   is Mon 9, and the code freeze is Tue 10. nfr-bench-1 is on its own VM, so no step here waits
   for it (the entry of 15:59:27).
