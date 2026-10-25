---
id: LG-8242
family: ledger
title: WK-1178 slice S4 — FD-1754, a pinned GBM in a model_call refuses every non-IDENTITY Factor type (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-25
owner: executor
tree: 8ac770f545eb66ef3677576e210f147ed85cb401
phase: P2
work: WK-1178
plans: [PL-8227]
corrected_by: []
relates: [FD-1754, PL-8227, FR-222, FR-240]
---

# LG-8242 — WK-1178 slice S4: FD-1754, a pinned GBM refuses every non-IDENTITY Factor type

Working id 8242 (LG), reserved 2026-10-25 22:41:48 UTC by lead 28 in `eta.md`; the slice's `SL-` id is not reserved yet (ids are minted at S4's merge turn, after FD 8233's block). Written by `exec-s4lg` before the audit, from the channel files `from-lead-2026-10-09.md` and `to-lead.md`, so the auditor reads the lines here and not in chat. Branch `draft/s4-fd1754`, code head `8ac770f545eb66ef3677576e210f147ed85cb401` (tree `1cf92667fb902632e68d8be1747fba7570cbca79`, merge-base `01a28e6d`). Every line below is quoted from the file and line named after it.

**GO:** the maintainer's entry "2026-10-25 21:17:38 GMT — Maintainer: S4 (FD-1754) GO; §14 re-mint @4949f946 PRE-VERIFIED (one line owed)" (`to-lead.md:31050`), first paragraph: "**S4 GO.** Code head `draft/s4-fd1754` @8ac770f5 (merge-base 01a28e6d; 8 files; `03-rating-engine.md`:110 carries its two escaped pipes; the format commit touches the refusal test only, S4's own lines, main's untouched per (B) as refined)." Its conditions (`to-lead.md:31051`): "(a) the 6-fit probe runs in a gap or under the load bound via run-heavy; (b) `test_rating_gbm_banded_save.py` in a scratch-DB gap (createdb → alembic → pytest → dropdb) with its rc line + sha; (c) full code gate in a free slot after FD 8233's (gate order = FD 8233 then S4 unless 8233 is not ready when a slot frees — then S4 takes it and 8233 follows); (d) ids minted at its merge turn, after FD 8233's block; (e) red/green/gate lines in its LG before the auditor is seated."
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-8227` (draft, `origin/draft/pl-8227` @`d1ac13aa`, `docs/plans/PL-08227-wk-1178-open-high-findings-s1a-s1b-fd-1729-split-s2-fd-1610-limb-2-s4-fd-1754-gbm-factor-read-plan-delta.md`), the row for S4 in its Tasks table: "| 1 | **S4** — FD-1754: the four unread GBM Factor types | Tasks S4-0 to S4-3 | `03` §3: FR-222 (the 2026-10-16 amendment), FR-240 (its 2026-10-16 amendment) | PL-1856 slice A (#1368) merged | B (pricing-core modelling) | no | ½ day |". Its Acceptance Standard item 18 is the probe (INTERACTION, SPLINE, POLYNOMIAL, EXPRESSION on xgboost and lightgbm: `model_call` premium against `predict_gbm(..., factors=<real Factors>)`; the result per type and backend goes in this ledger). Item 19 is "If a type differs silently: it is added at `factors.py:546`".

Requirements covered: FR-222 (a dated clause, `docs/specs/03-rating-engine.md`:110) and FR-240 (a dated clause, `03-rating-engine.md`:140). Finding: FD-1754 (`docs/findings/FD-01754-a-gbm-model-call-on-a-banded-or-grouped-factor-scores-with-factors-empty-over-the-graphs-raw-value.md`).

The plan's S4-2 lists a narrower write set (`factors.py`, the save test, the FR-222 row). The rulings below widened it; they are quoted in the Build log:

- (1) `to-lead.md` entry "2026-10-25 13:07:06 GMT" (relayed in `from-lead-2026-10-09.md:7726`): option (b), refuse every non-IDENTITY Factor type for a pinned GBM in a `model_call`; the exact-message test and the compile message change together (common seat brief item 13).
- (2) "2026-10-25 15:38:26 GMT — Maintainer: S4 refusal-message wording ADOPTED" (`to-lead.md:30732`).
- (3) "2026-10-25 16:49:23 GMT" (`to-lead.md:30799`): the backend save-check 422 text, option (a).
- (4) "2026-10-25 16:56:47 GMT" (`to-lead.md:30825`): the FR-240 spec gap, a dated clause in the same branch.

The diff against merge-base `01a28e6d` is 8 files, +363/−32 (`git diff --stat 01a28e6d 8ac770f5`): `backend/src/app/errors.py`, `backend/src/app/platform/rating_algorithms.py`, `backend/tests/test_rating_gbm_banded_save.py`, `docs/INDEX.md`, `docs/specs/03-rating-engine.md`, `packages/pricing-core/src/pricing_core/modelling/factors.py`, `packages/pricing-core/src/pricing_core/rating/compile.py`, `packages/pricing-core/tests/test_rating_gbm_banded_refusal.py`.

### Task list

Branch history, oldest first (`git log --oneline c14c9c4a^..8ac770f5`):

1. S4-1, RED `c14c9c4a` — `test(pricing-core): FD-1754 S4 — red tests: a pinned GBM's non-IDENTITY Factors are refused (draft, unrun)`. One file, `test_rating_gbm_banded_refusal.py`.
2. S4-2, FIX `853dcbcb` — `fix(pricing-core,specs): refuse every non-IDENTITY Factor type for a pinned GBM in a model_call (FD-1754, S4)` (`factors.py` filter `is not IDENTITY`, the compile message, the exact-message test tail, the `03` FR-222 clause).
3. SAVE `4a919eca` — `fix(backend): the save-check 422 names transformed Factors, not banded or grouped (S4, FD-1754)` (ruling 16:49:23).
4. SPEC `5db869ea` and `0a45befb` — `03` FR-240 dated clause, then its slug (kind) in code form (ruling 16:56:47).
5. `5ae9f692` — `docs(specs): 03 FR-222 — escape the pipes in the S4 clause (check 22)`.
6. `006ff4fd` — `docs(index): regenerate (check 39)`.
7. `8ac770f5` — `style(tests): ruff format S4's own lines in the refusal test` (S4's own lines only; main's unformatted lines untouched, per (B) as refined).

Acceptance checks are the red, green and gate lines in the Gate section below.

### Gate

**RED** at `c14c9c4af385dbaff2ded27370b390acf592be25` (tree `af74ab42`, base `01a28e6d`; detached worktree `s4-red`; exec-s4check, via run-heavy, no slot held). Source: `from-lead-2026-10-09.md:7956`: "**S4 gap evidence (exec-s4check, stopped):** RED c14c9c4a refusal file '11 failed, 9 passed' rc 1 (tests bite: the exact-message test, 6 E/I probes, 4 compile refusals)". Accepted at `to-lead.md:31033`: "RED @c14c9c4a `11 failed, 9 passed` rc 1 (the exact-message test, the 6 E/I probes, the 4 compile refusals bite)". The red tests were first written unrun at 15:38:00 GMT (`from-lead-2026-10-09.md:7820`).

**GREEN, refusal file plus raise sites** at `0a45befb` (before the pipe-escape, INDEX and format commits). Source: `from-lead-2026-10-09.md:7956`: "GREEN 0a45befb refusal + raise-sites '39 passed' rc 0; ruff check 0; mypy 'Success: no issues found in 249 source files' 0; req-coverage 0 (FR-222 34 files, FR-240 46); **ruff format --check 1** (the 2 new test files; errors.py/compile.py pre-existing on main); **audit-docs 1: check 22 at 03:110 — unescaped pipes in the S4 FR-222 clause ('B | A' / 'A | B')**". Both defects were fixed by `exec-s4fix2` (commits 5, 6 and 7 above).

**GREEN at the gate head** `8ac770f545eb66ef3677576e210f147ed85cb401` (`from-lead-2026-10-09.md:7966`): "**S4 READY @8ac770f545eb66ef3677576e210f147ed85cb401** (exec-s4fix2 stopped): 5ae9f692 pipes escaped (check 22), INDEX regenerated (check 39), S4's own lines ruff-formatted only (18 opcodes taken, 18 skipped; deletions vs main still 5); audit-docs rc 0 'All checks passed.', ruff check 0, format intersection (touched ∩ added) 0 in both test files, run-small 39 passed." The GO restates them (`to-lead.md:31051`): "audit-docs 0 @8ac770f5; ruff 0; mypy 0 (249 files); req-coverage FR-222 34 / FR-240 46; fixture grep 0", GREEN 8ac770f5 "39 passed". The fixture grep found no existing fixture or demo data newly refused (`to-lead.md:31033`).

**Probe (Acceptance 18, six fits)** at `8ac770f545eb66ef3677576e210f147ed85cb401`, worktree `s4-draft`, porcelain 0, load1 2.16, run by the lead under `run-heavy --grant '2026-10-25 21:17:38 GMT'` (`from-lead-2026-10-09.md:7978`): "`pytest -q -rA packages/pricing-core/tests/test_rating_gbm_banded_refusal.py -k prices_as_predict_gbm_or_is_refused` rc 0 '6 passed, 14 deselected in 2.28s' — E-a / E-b / I-cell-swapped × xgboost / lightgbm all PASSED (= refused at compile, or priced exactly as predict_gbm(factors=real)); log scratch/s4-probe-8ac7.log." Accepted at `to-lead.md:31074` (entry "2026-10-25 21:51:49 GMT"): "S4 probe verified in `scratch/s4-probe-8ac7.log`: 6 PASSED lines, "6 passed, 14 deselected in 2.28s", rc 0, under run-heavy grant 21:17:38, load1 2.16 — accepted."

**banded_save, scratch DB** at `8ac770f545eb66ef3677576e210f147ed85cb401` (`from-lead-2026-10-09.md:7991`): "S4 (exec-s4savedb, FINAL 22:17): test_rating_gbm_banded_save.py "10 passed, 1 warning in 0.71s" @8ac770f5, container s4-pg-8ac770f5 (127.0.0.1:32769; postgres:16-alpine 75f5a96988cd), alembic upgrade head rc 0, run-heavy rc 0 under grant 22:13:28; rm -fv rc 0; ps -a filter empty; dangling volumes 16 → 16; redis db13 dbsize 0. Seat stopped." Accepted at `to-lead.md:31104` (entry "2026-10-25 22:18:25 GMT"): "`test_rating_gbm_banded_save.py` "10 passed, 1 warning in 0.71s" in `s4-pg-8ac770f5` (127.0.0.1:32769, image 75f5a96988cd), alembic head 0, rm -fv 0, ps filter empty, dangling 16 → 16, db13 0 — accepted. **S4 now owes only the full code gate**".

**Full code gate** — pending: gate START 2026-10-25 22:20:51 UTC on gate-1 (`from-lead-2026-10-09.md:8002`): "S4 GATE START: slot gate-1, flock PID 3028745. Script scratch/s4-gate/s4-gate.sh (sha256 52deebb24b24…), derived from fd8233-gate.sh a5acb997 by substitution only (11 lines: header, W, L, the inner guard ×2 plus flock path, DB names ×4, branch). prelaunch rc 0. START line "START head: 8ac770f545eb66ef3677576e210f147ed85cb401 tree: 1cf92667fb902632e68d8be1747fba7570cbca79 branch: draft/s … 2026-10-25T22:20:51+00:00 1.66". Launched setsid nohup under to-lead 22:18:25." The END line and the rc table are to be appended by the lead after the gate's END; none is written here.

2026-10-25 23:32:20 GMT — superseded by the gate of record below (the placeholder line above is kept, not edited).

**Gate of record** at `8ac770f545eb66ef3677576e210f147ed85cb401`, each line verbatim from `~/gi-pricing-plan.local/scratch/s4-gate/gate/gate.log` (74 lines) with its line number:

```text
L1: START head: 8ac770f545eb66ef3677576e210f147ed85cb401 tree: 1cf92667fb902632e68d8be1747fba7570cbca79 branch: draft/s4-fd1754 load(date l1 l5 l15): 2026-10-25T22:20:51+00:00 1.66 2.03 2.18
L25: | ruff | rc=0 |
L26: | mypy | rc=0 |
L27: | import_linter | rc=0 |
L28: | audit_docs | rc=0 |
L29: | req_coverage | rc=0 |
L30: | contracts | rc=0 |
L31: | pytest | rc=0 |
L32: pytest summary: 6806 passed, 21 skipped, 147 warnings in 2561.98s (0:42:41)
L34: | pnpm install --frozen-lockfile | rc=0 |
L35: | pnpm generate:api | rc=0 |
L36: | pnpm lint | rc=0 |
L37: | pnpm type-check | rc=0 |
L38: | pnpm test --maxWorkers=2 | rc=0 |
L39: | pnpm build | rc=0 |
L52: | demo | designed stop at 2026-10-25T23:24:11+00:00 (both lines seen) |
L53: | demo.py --journey wf-699 | rc=0 |
L54: | demo seconds | 945 |
L57: | D7 | ok  19985 policies in the sample; rate table edits: +485990825; NCD ladder and expense loading: +3851186; sum +489842011 minor units (full-book attribution cost: FD-1576) |
L60: | postgres | StartedAt 2026-10-25T16:25:17.035473218Z | PortBindings {"5432/tcp":[{"HostIp":"","HostPort":"5432"}]} | working_dir /home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/tools-main/deploy (under tools-main) |
L61: | redis | StartedAt 2026-10-25T16:25:16.939049123Z | PortBindings {"6379/tcp":[{"HostIp":"","HostPort":"6379"}]} | working_dir /home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/tools-main/deploy (under tools-main) |
L62: | minio | StartedAt 2026-10-25T16:25:16.98858877Z | PortBindings {"9000/tcp":[{"HostIp":"","HostPort":"9000"}],"9001/tcp":[{"HostIp":"","HostPort":"9001"}]} | working_dir /home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/tools-main/deploy (under tools-main) |
L63: | keycloak | StartedAt 2026-10-25T23:24:19.61675574Z | PortBindings {"8080/tcp":[{"HostIp":"","HostPort":"8080"}]} | working_dir /home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/tools-main/deploy (under tools-main) |
L72: | zeros | own-DB count=0 redis RT db 1 dbsize=0 redis RD db 3 dbsize=0 |
L73: | END rc parts | python max=0 fe max=0 demo=0 restore rc_kc=0 |
L74: END 2026-10-25T23:24:52+00:00 3.85 2.59 2.85 (date l1 l5 l15) rc=0
```

Gate of record accepted: to-lead 2026-10-25 23:25:50 GMT

### Audit

Pending. The slice audit is `RS 8243` (reserved 2026-10-25 22:41:48 UTC for the auditor at gate head `8ac770f5`); the auditor's seat is placed at the gate's END. This section is a placeholder and carries no verdict.

### Build log

Appended per task and per push, never rewritten.

- 2026-10-25 15:38:00 GMT — RED `c14c9c4a` drafted, not run (`from-lead-2026-10-09.md:7820`).
- 2026-10-25 13:07:06 GMT ruling (1) — option (b) and the item 13 message change (`from-lead-2026-10-09.md:7726`). 15:38:26 GMT — message wording adopted (`to-lead.md:30732`).
- 2026-10-25 16:48:23 GMT — `853dcbcb` verified on origin (`from-lead-2026-10-09.md:7860`); 16:49:23 GMT — save-check ruled (a); 16:55:56 GMT — `4a919eca` (`from-lead-2026-10-09.md:7866`); 16:56:47 GMT — FR-240 ruled (a); 17:02:30 GMT — `0a45befb` final (`from-lead-2026-10-09.md:7874`).
- 2026-10-25 21:06:06 GMT — gap evidence accepted, two defects sent to `exec-s4fix2` (`to-lead.md:31033`); 21:09:41 GMT — `5ae9f692` pushed (`from-lead-2026-10-09.md:7961`).
- 2026-10-25 21:17:38 GMT — S4 GO (`to-lead.md:31050`). 21:51:49 GMT — probe accepted. 22:18:25 GMT — banded_save accepted, gate slot decision `gate-1`. 22:20:51 UTC — gate START (`from-lead-2026-10-09.md:8002`).
- 2026-10-25 22:4x UTC — this ledger written by `exec-s4lg` on branch `s4-lg-8242`, from `8ac770f5`, docs only. The lead folds it onto `draft/s4-fd1754` after the gate's END.

## PRs

None yet. The PR title convention applies at the PR: `SL-<n>: …` once the slice's id is minted.
