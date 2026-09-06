---
id: RL-887
family: ruling
title: Finding 3: the framing was wrong, and the class is bigger and mostly benign
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slices-2-4-rulings.md
---

## RL-887 — Finding 3: the framing was wrong, and the class is bigger and mostly benign

**The correction leads, per `docs/process/delivery-process.md` §15: my own filing of this finding
in `2026-08-29-w11-slice2-rulings.md` was wrong in its framing.** It reported
`GOLDEN_QUOTE_MISMATCH` being owned by `03` §5.1 and registered nowhere as a defect. It is not
one. `PlatformError.__init__` (`backend/src/app/errors.py:335-348`) refuses an unknown code with
the message *"Codes are enumerated in the owning spec's Interfaces section; **add it there before
raising it**"* — the registry is deliberately populated at the point of first **raise**,
spec-first. A declared-but-unregistered code is the designed state until something raises it.
`GOLDEN_QUOTE_MISMATCH` is WK-672's to register when WK-672 raises it, and nothing is wrong today.

**Measured rather than exemplified.** Across the seven module specs' owned-code blocks, **32 of
161 declared codes are unregistered**: `01` 0/17, `02` 5/58, `03` 11/36, `04` 9/9, `05` 7/7,
`06` 0/15, `07` 0/19. `04` and `05` are 9/9 and 7/7 because neither module is built — which is
the mechanism working, not a backlog. The enumerating command, so this number is re-derivable
rather than quoted: extract `` `UPPER_SNAKE` `` tokens from each spec's
`**Error codes owned by this module:**` block and diff against the string literals in
`backend/src/app/errors.py`. The subset that would matter is codes whose owning workstream has
**closed**, and the sweep finds exactly one — see the finding below.

**Ruled: no spec change, no register row, and no defect.** The two codes this record's own work
adds to the unregistered count — `MODEL_CALL_FAILED` (RL-877) and `NO_LIVE_RATING_VERSION`
(RL-880) — are pending their raise in Slice 1 and Task 2.1 respectively, which is the
mechanism behaving as designed.

**Acceptance test.** The ruling is "no change", so the test is the standing one it establishes:
**an audit that books an unregistered spec-declared code as a defect without first checking
whether the workstream that owes its raise has shipped has mis-applied this ruling.** What the
measurement makes newly expressible is the sharper statement — *"a module spec declares an error
code that its own **closed** workstream never raises"* — which is now countable rather than
anecdotal, and which returns exactly one hit today.

---

## Findings reported, not ruled

**1. `FR-240`'s control-factor clause appears to be enforced nowhere, and WK-669 closed.**
FR-240 (`03:136`) requires bundle compilation to validate, among other things, *"no
`control`-intent factor in a rateable path (`02` FR-88)"*, and `03` §5.1 owns
`CONTROL_FACTOR_IN_RATEABLE_PATH` for it. At `c049159` that code appears in no Python file, and
`git grep -in "intent" -- packages/pricing-core/src/pricing_core/rating/` returns **zero** — a
true negative, positive-controlled by `git grep -c "def " -- .../rating/compile.py` returning
`15` over the same pathspec. The only `FactorIntent.CONTROL` hits in the repository are `02`
modelling tests. FR-240 is WK-669's (`../roadmap.md:374`) and **WK-669 closed 2026-08-27**. Whether
this reopens the WK-669 close, becomes a register row with an owner, or is absorbed by WK-671's compile
path is a scope question, and `CLAUDE.md` §12 puts scope outside this role.

**2. Checked and clear, recorded so nobody re-raises it.** `07` FR-422 (`07:116`) cites
FR-243 beside FR-268 for *"the rating `Bundle` cache"*, which reads like a stranded
list-mate of the Redis-caching glossary error that `ddb0c6f` (#340) fixed. It is not:
`git log -S` shows that commit **added** the cross-reference in the same edit as the fix, and
the cached thing FR-422 names is the `Bundle`. No finding.

---

## Sources — read at `c049159`, and measured where a measurement is claimed

- `docs/specs/03-rating-engine.md` — §2 glossary `:67`, FR-239/240 `:135-136`, FR-243
  `:139`, §8 `:756-777`, §9 `:780-800`, §5.2 `:601-616`.
- `docs/specs/06-governance.md` — FR-347 `:83`, §3.3 `:105-149`, §4.2 `:251-348`.
- `docs/specs/07-platform.md` — FR-422 `:116`, FR-413 `:102`.
- `docs/rulings/RL-00867-compiledbundle-is-spec-only-bundle-is-the-only-thing-that-exists-and-they-are-not-the-same-type.md` RL-867 and its addendum;
  `2026-08-29-w11-slice1-rulings.md` Rulings 8 and 10;
  `2026-08-29-w11-slice2-rulings.md` Rulings 14 and 15;
  `2026-08-29-w11-slices-2-4-planning-readiness.md` §3.3, §3.4, §4, §9, §10, §11.
- `.importlinter` in full; `docs/adrs/ADR-00703-pricing-core-is-dependency-free-and-owns-all-actuarial-maths.md`.
- Code: `packages/model-schema/src/model_schema/approvals.py`, `.../permissions.py`,
  `packages/pricing-core/src/pricing_core/rating/compile.py`,
  `.../modelling/gbm.py`, `backend/src/app/errors.py`, `.../platform/approvals.py`,
  `.../platform/diff_cache.py`, `.../api/service_accounts.py`, `.../api/deps.py`,
  `.../auth/service.py`, `.../main.py`, `.../config.py`, `backend/tests/test_rbac.py`,
  `backend/tests/test_approvals.py`.
- Measured this session against `/home/puzhenhao1989/gi-pricing-plan/.venv` (FastAPI 0.141.1,
  pydantic-core 2.46.4): the `ORJSONResponse` deprecation and its render-time assertion; the
  annotated-route outbound-validation probe; the raw-`Response` and `model_dump_json` probes;
  and the 0.0168 ms/call serialisation figure, whose limits are stated in RL-883.
