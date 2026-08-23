# W32-2 — the validation rule catalogue: execution ledger

What executing
[`2026-08-23-w32-2-validation-rule-catalogue.md`](2026-08-23-w32-2-validation-rule-catalogue.md)
actually did, on 2026-08-23, the same day the plan was written.

The plan is **not** edited to agree with this file — [`README.md`](README.md) has that rule.
Where the plan was wrong, this record says so and the correction lives here.

**Executed by one subagent in an isolated worktree**, as one of five W32 slices run
concurrently. The slice map recorded all five as independent, and this one proved it: three
commits, no cross-slice edit, one Alembic migration.

---

## Result

| | Before | After |
|---|---|---|
| Named rules reaching a workspace | 0 seeded | **38 of 38** |
| `FR-DATA-53` | unallocated | defined, routed, evidenced |
| Alembic head | `9e4c7b21fa08` | `7c1a9e40b3d2` |

The catalogue axis this slice owned is complete. `scripts/scope-audit.py DATA --catalogue VR`
reports `TOTAL 38/38`.

---

## The acceptance instrument was wrong, and the code was right

The plan's closing step asked for `38/38` **and** exit 0 from the same `scope-audit.py`
invocation. That pair is unachievable, and not because of anything this slice did.

`scripts/scope-audit.py` returns `1` as soon as any in-scope requirement lacks test
evidence, and it does so **before** the catalogue result is consulted. A slice whose own
declared scope leaves `FR-DATA-52`, `NFR-DATA-1` and `NFR-DATA-2` untouched therefore cannot
produce exit 0, however complete its catalogue is.

The two numbers answer different questions. `38/38` is catalogue completeness — this slice's
deliverable. Exit 0 is whether the whole DATA module is closed — a
[`CLAUDE.md`](../../CLAUDE.md) §13 question that no single slice can settle. The plan
conflated them.

**Verdict: the plan was wrong, the code is right.** Recorded here rather than fixed in the
plan, and `scope-audit.py` is left alone.

## Four more places the plan did not match the repository

| Plan said | Repository |
|---|---|
| A check constraint `builtin = (catalogue_id IS NOT NULL)` | Not expressible — a workspace rule may carry a catalogue reference without being built in. Relaxed to `builtin IS FALSE OR catalogue_id IS NOT NULL` |
| `_headers(READ_ROLE)` and a `NO_READ_ROLE` fixture | Neither exists in this suite |
| A `FORBIDDEN` error code | The code is `PERMISSION_DENIED` |
| Ordering unspecified | Pinned to `id ASC`, so the response is reproducible |

## A decision the plan did not reach

The catalogue is seeded from `grant` in `backend/tests/conftest_db.py`, beside
`seed_builtin_roles`. A workspace in this schema is a bare `UUID` column rather than a row,
so `grant` is the only workspace-creation path the suite has. The catalogue arrives with the
workspace exactly as the roles do, and for the same reason.

## Verification

Every gate command exit 0, each read from its own exit code.

The full suite's first run was killed at 24% by the background-task manager and its
replacement was detached, leaving it the one command without a captured code. It was re-run
to completion in a quiet window before landing: **exit 0, 1788 passed, 1 skipped, 1 xfailed,
7:34 at load 1.5**. The single skip is infrastructure-conditional and not the database —
`conftest_db.py` skips at fixture level, so an unreachable database would have skipped dozens.

## Carried forward, with owners

- `examples/fremtpl2/seed.py` still fabricates a `dry_run_report_id` for its nine workspace
  rules. Removing it needs a real dry-run report the seed does not produce. **Unowned.**
- `frontend/src/api/profiles.ts` still hard-codes `VR-DST-1`'s PSI bands. **Owner: W6b-13.**
- `FR-DATA-52`, `NFR-DATA-1` and `NFR-DATA-2` remain unevidenced, out of this slice's scope
  and carrying written verdicts in [`../roadmap.md`](../roadmap.md).
