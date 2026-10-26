---
id: RS-1926
family: research
kind: audit
title: S4 (WK-1178, FD-1754) slice audit — a pinned GBM in a model_call refuses every non-IDENTITY Factor type, at gate head 8ac770f5
status: draft
created: 2026-10-25   # drafted 2026-10-25 under working id 8243; created = mint date
owner: auditor
tree: 4b55f6a611147e8ffa1e16c43e4b9efcd6ecaaff
phase: P2
work: WK-1178
corrected_by: []
relates: [LG-1925, FD-1754, FR-222, FR-240]
---

# RS-1926 — S4 slice audit (FD-1754, the GBM `model_call` refusal)

*(Working id 8243, reserved by lead 28; the slice is SL-1924 and its ledger LG-1925, both unminted at this audit. Written by `aud-s4` (auditor, sonnet, effort medium) in worktree `.claude/worktrees/aud-s4`, branch `aud-s4-2026-10-25`, from `4b55f6a6`. Docs and diff reading only: no test, gate or audit-docs run by this seat. The verdict below is a proposal; the lead adopts it.)*

## Question

Does `draft/s4-fd1754` at the gate head `8ac770f5` (merge-base `01a28e6d`, with LG-1925 folded at `3ba98b0b` and the gate lines at `4b55f6a6`) meet every clause of the S4 GO (`to-lead.md:31050-31051`), PL-1927 row 1 and FD-1754's open limb, and is the evidence in LG-1925 reachable and honest?

## Method

Scope first, from the GO, PL-1927 row 1 and FD-1754; then evidence.

- **GO**, verbatim heading and first paragraph (`to-lead.md:31050-31051`): "## 2026-10-25 21:17:38 GMT — Maintainer: S4 (FD-1754) GO; §14 re-mint @4949f946 PRE-VERIFIED (one line owed)" / "**S4 GO.** Code head `draft/s4-fd1754` @8ac770f5 (merge-base 01a28e6d; 8 files; `03-rating-engine.md`:110 carries its two escaped pipes; the format commit touches the refusal test only, S4's own lines, main's untouched per (B) as refined). Evidence accepted as stated: RED c14c9c4a "11 failed, 9 passed"; GREEN 8ac770f5 "39 passed"; audit-docs 0 @8ac770f5; ruff 0; mypy 0 (249 files); req-coverage FR-222 34 / FR-240 46; fixture grep 0. Conditions: (a) the 6-fit probe runs in a gap or under the load bound via run-heavy; (b) `test_rating_gbm_banded_save.py` in a scratch-DB gap (createdb → alembic → pytest → dropdb) with its rc line + sha; (c) full code gate in a free slot after FD 8233's …; (d) ids minted at its merge turn, after FD 8233's block; (e) red/green/gate lines in its LG before the auditor is seated."
- **PL-1927 row 1** (`origin/draft/pl-8227`, `docs/plans/PL-01927-…-plan-delta.md`): "| 1 | **S4** — FD-1754: the four unread GBM Factor types | Tasks S4-0 to S4-3 | `03` §3: FR-222 (the 2026-10-16 amendment), FR-240 (its 2026-10-16 amendment) | PL-1856 slice A (#1368) merged | B (pricing-core modelling) | no | ½ day |"; Acceptance 18 (the probe, four types × two boosters, result per type in the LG) and 19 (a silently differing type is added at `factors.py:546`); its dated delta line for row 1 (S4 = SL-1924, LG-1925, SL row mints at S4's turn in its own PR).
- **FD-1754** on `origin/main` (`docs/findings/FD-01754-…`), Disposition item 4: "Open limb, for the planner and the maintainer: interaction, spline, polynomial and expression Factors on a GBM may carry the same latent defect … this has not been read or run."
- **Code**: `git diff $(git merge-base 8ac770f5 origin/main) 8ac770f5 --stat`, then each source file and the spec hunks (word-diff). Docs-only delta: `git diff 8ac770f5 4b55f6a6 --stat`.
- **Evidence lines**: each LG-1925 channel cite read at its line (`from-lead-2026-10-09.md`, `to-lead.md`), the quoted strings matched with `grep -F`; `merge-base --is-ancestor` for the SHAs; the gate of record diffed against `scratch/s4-gate/gate/gate.log`.

## Findings

**Proposed verdict: CLEAN.** No blocking finding. Five non-blocking (N1–N5), none holding the merge.

### Scope against the diff

- `git diff 01a28e6d5571ed8f8d478760fc11aa2015326840 8ac770f5 --stat` = 8 files, +363/−32: `backend/src/app/errors.py` (comment), `backend/src/app/platform/rating_algorithms.py` (docstrings + 422 title/detail), `backend/tests/test_rating_gbm_banded_save.py` (+ expression case), `docs/INDEX.md`, `docs/specs/03-rating-engine.md` (lines 110, 140), `packages/pricing-core/src/pricing_core/modelling/factors.py`, `…/rating/compile.py`, `packages/pricing-core/tests/test_rating_gbm_banded_refusal.py` (+315/−5). Matches the GO's "8 files" and LG-1925's list.
- `git diff 8ac770f5 4b55f6a6 --stat` = exactly two paths: `docs/INDEX.md` (+1) and the LG-1925 file (+120). No other path.
- The core change is one expression, `factors.py` `gbm_transformed_factors`: `tuple(f for f in factors if f.type is not FactorType.IDENTITY)` (was BANDING/GROUPING only). The two callers (save check `_refuse_gbm_transformed_factors`, compile `check_model_call_gbm_factors`) take it unchanged: one definition, both points. The messages change in both (`"fitted on transformed Factors [<slug> (<kind>), …] … (FR-222, FR-240)"`) and the save 422 title is `A model_call cannot score a GBM fitted on transformed Factors`.
- `FactorType` (`model_schema/modelling.py:89-99`): IDENTITY, BANDING, GROUPING, INTERACTION, SPLINE, POLYNOMIAL, OFFSET, EXPRESSION. `factors.py:11-27` (docstring at the gate head): `spline`/`polynomial` are refused by name at resolution (not built) and `offset` is superseded and refused, so a GBM cannot be fitted on those three; they are not a regression surface of `is not IDENTITY`. EXPRESSION and INTERACTION are the two types that resolve and were scored silently — the two the tests probe.

### GO clauses

| Clause | Met | Evidence |
|---|---|---|
| 8 files, merge-base `01a28e6d`, format commit touches the refusal test only | yes | `merge-base` printed `01a28e6d5571…`; `git show --stat 8ac770f5` = 1 file, `test_rating_gbm_banded_refusal.py` (117+/42−) |
| `03`:110 carries its two escaped pipes | yes | the FR-222 clause text in `03-rating-engine.md:110` reads `"B \| A"` / `"A \| B"` (word-diff); audit-docs rc 0 at L28 of the gate log |
| RED c14c9c4a "11 failed, 9 passed" | yes, relayed | `from-lead-2026-10-09.md:7956`; accepted `to-lead.md:31033`; both quoted strings match by `grep -F`. 11+9 = 20 = the refusal file's 6 probe + 14 other tests (the probe log's "6 passed, 14 deselected") — consistent. Not re-run (ban). See N3 |
| GREEN "39 passed" | yes, relayed | `from-lead-2026-10-09.md:7956` (at `0a45befb`) and `:7966` (at `8ac770f5`, "run-small 39 passed"); `to-lead.md:31033` |
| audit-docs 0, ruff 0, mypy 0 (249 files), req-coverage 34/46, fixture grep 0 | yes | same lines; at the gate head the full gate re-ran them: L26 mypy rc=0, L25 ruff rc=0, L28 audit_docs rc=0, L29 req_coverage rc=0 |
| (a) 6-fit probe via run-heavy | met | `from-lead-2026-10-09.md:7978`; accepted `to-lead.md:31073-31074`; `scratch/s4-probe-8ac7.log` line 1 "run-heavy: slot(s) held: gate-1; running under grant to-lead 2026-10-25 21:17:38 GMT", lines 6–11 six PASSED (E-a, E-b, I-cell-swapped × xgboost, lightgbm), line 12 "6 passed, 14 deselected in 2.28s" |
| (b) `test_rating_gbm_banded_save.py` scratch DB, rc line + sha | met | `from-lead-2026-10-09.md:7991` ("10 passed, 1 warning in 0.71s" @8ac770f5, `s4-pg-8ac770f5`, alembic rc 0, rm -fv rc 0); accepted `to-lead.md:31103-31104` |
| (c) full code gate in a free slot | met | gate-1, `from-lead-2026-10-09.md:8002`; END read by the lead `to-lead.md:31209` ("GREEN … gate of record for S4 at 8ac770f5") |
| (d) ids minted at merge turn | open, by design | LG-1925 and this RS are working ids; SL-1924 / LG-1925 / RS-1926 mint at S4's turn (owed list) |
| (e) red/green/gate lines in the LG before the auditor | yes | LG-1925 §Gate carries RED, GREEN ×2, probe, banded_save and the gate of record, each with sha and rc |

### Red-first and reachability

`git merge-base --is-ancestor` (tree `aud-s4` at `4b55f6a6`): `c14c9c4a`→`0a45befb` rc 0; `0a45befb`→`8ac770f5` rc 0; `c14c9c4a`→`8ac770f5` rc 0; `8ac770f5`→`4b55f6a6` rc 0. `git log --oneline c14c9c4a^..8ac770f5` = the 7 commits LG-1925 lists, red first (`c14c9c4a` is test-only: the refusal file alone), then `853dcbcb` fix, `4a919eca` save, `5db869ea`/`0a45befb` FR-240, `5ae9f692` pipes, `006ff4fd` INDEX, `8ac770f5` format. Every SHA the LG cites as evidence is reachable from the gate head.

### Channel cites in LG-1925 (each read at its line)

`from-lead-2026-10-09.md`: 7726 (ruling 1, option (b)), 7820 (red drafted 15:38:00), 7860, 7866, 7874, 7956 (red/green), 7961, 7966 (S4 READY), 7978 (probe), 7991 (banded_save), 8002 (gate START) — each is the cited entry. `to-lead.md`: 30732 (15:38:26), 30799 (16:49:23), 30825 (16:56:47), 31033 (evidence accepted; heading 31031), 31074 (probe; heading 31073), 31104 (banded_save; heading 31103), 31050/31051 (GO) — each is the cited entry. All eleven quoted evidence strings matched verbatim by `grep -F` against the channel files.

### Gate of record against `gate.log`

The 26 `L<n>:` lines in LG-1925 §"Gate of record" (L1, L25–L32, L34–L39, L52–L54, L57, L60–L63, L72–L74) were extracted from the LG and compared with `sed -n <n>p` of `scratch/s4-gate/gate/gate.log` (74 lines) for the same numbers: `diff` rc 0 — identical, line for line, including the L-numbers. L1 head `8ac770f545eb66ef3677576e210f147ed85cb401` / tree `1cf92667…` equals the gate head's tree (`git rev-parse 8ac770f5^{tree}`); L74 `END … rc=0`; L73 `python max=0 fe max=0 demo=0 restore rc_kc=0`; L63 keycloak bind under tools-main. The lead's reading of the same lines is `to-lead.md:31209`.

### Spec lines (`03`, append-only)

- FR-222 (`03:110`): one dated clause appended — "*(Amended 2026-10-25, WK-1178, S4, FD-1754, on the entry headed "2026-10-25 13:07:06 GMT — …", decision (1) option (b), and decision (2) with the wording adopted by the entry headed "2026-10-25 15:38:26 GMT — …": the `Known gap` refusal above applies to a GBM fitted on Factors of any type other than `identity` …)*". It explicitly supersedes only the sentence that a GBM on Factors "neither banded nor grouped is not either" for `expression` and `interaction`; keying on the step, the GLM exemption and the `GbmFitError` rule stand. Both cited entries exist (`to-lead.md:30601`, `:30732`).
- FR-240 (`03:140`): one dated line appended, "*(Amended 2026-10-25 by the maintainer (dated line by delegation), WK-1178 S4, FD-1754 (to-lead 13:07:06, 16:56:47): …)*"; the 16:56:47 entry exists (`to-lead.md:30825`).
- Append-only: for both rows the old text (less its trailing ` |`) is a strict prefix of the new row (Python prefix check on `01a28e6d` vs `8ac770f5`); the other 1,613 lines are identical. The barred word does not appear in any added line or commit message of `01a28e6d..4b55f6a6`.

### Findings

- **N1 (non-blocking) — the error catalogue in `03` is not amended.** `03-rating-engine.md:1165` (the `MODEL_CALL_GBM_TRANSFORMED_FACTOR` entry, "*(added 2026-10-16 … a `model_call` step pins a GBM fitted on a banded or grouped Factor …)*") still says banded or grouped; S4 amends FR-222 and FR-240 only. The FR clauses govern and the catalogue is not wrong about what it names, but it reads narrower than the code. Suggested: one dated append at the catalogue entry at mint, or a pointer to FR-222's clause. Evidence: `git -C aud-s4 grep -n 'MODEL_CALL_GBM_TRANSFORMED_FACTOR' 4b55f6a6 -- docs/specs` and `sed -n 1165p`.
- **N2 (non-blocking) — Acceptance 18 asks a verdict per type; the LG gives two of four.** PL-1927 item 18 names INTERACTION, SPLINE, POLYNOMIAL, EXPRESSION × both boosters, "its result per type and backend … in S4's `LG-`". The probe (`PROBES` E-a, E-b, I-cell-swapped) and LG-1925 cover EXPRESSION and INTERACTION. SPLINE and POLYNOMIAL cannot be fitted (`factors.py:11-27`: refused by name at resolution), so the omission hides no risk, but the LG states none of this. Suggested: one LG line quoting `factors.py:17-19` at mint.
- **N3 (non-blocking) — the red and green lines are relayed, not raw logs.** RED `11 failed, 9 passed` rc 1 and GREEN `39 passed` rc 0 are the lead's/exec-s4check's report lines (`from-lead-2026-10-09.md:7956`, `:7966`), accepted by the maintainer; no raw log carrying `head=<sha>` first and `rc=<n>` last (seat brief item 37) was found for them under `scratch/`. The probe log `scratch/s4-probe-8ac7.log` has a run-heavy banner as line 1 and no `head=` / `rc=` lines (rc 0 is only in the channel entry). This seat ran no test (ban), so these remain the lead's accepted evidence; they are internally consistent (20 = 11+9 = 6+14) and the full gate at the same head (L31, 6806 passed rc=0) re-ran the same files. Suggested: none for the merge; for later slices write the log's first/last line.
- **N4 (non-blocking) — LG-1925 still carries the "Audit pending" placeholder and the stale "Full code gate — pending" paragraph.** Both are append-only artefacts (the supersede line at LG 23:32:20 is present). The Audit section is to be completed by the fold of this record; no action beyond the usual mint fold (LG `Audit` cites RS-1926 at its turn).
- **N5 (non-blocking) — the pre-mint spec lines name unminted ids only in prose.** The FR clauses cite no working id (they cite channel stamps), so audit-docs checks 31/32 are unaffected; noted so the mint re-point sweep (`git grep -E "\bRS[ -]0?8243\b"`, `SL[ -]0?8245`, `LG[ -]0?8242`, whole tree) is not skipped. Pre-mint sweep results from this seat: see the FINAL message.

### Not done by this seat (stated, not hidden)

No test, audit-docs, mypy, ruff or gate was run (brief: docs + diff reading, grant none). Their results are those of the gate of record (L25–L31) at the same head, read line by line above. FR-222 34 / FR-240 46 req-coverage counts are the lead's accepted figures and the gate's `req_coverage rc=0` (L29).
