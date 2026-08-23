# W32-3 — dataset list derived fields: execution ledger

What executing
[`2026-08-23-w32-3-dataset-list-derived-fields.md`](2026-08-23-w32-3-dataset-list-derived-fields.md)
actually did, on 2026-08-23, the same day the plan was written.

The plan is **not** edited to agree with this file — [`README.md`](README.md) has that rule.
Where the plan was wrong, this record says so and the correction lives here.

**Executed by one subagent in an isolated worktree**, as one of five W32 slices run
concurrently. Seven commits, one Alembic migration that backfills and then promotes a column
to `NOT NULL`.

---

## Result

| | Before | After |
|---|---|---|
| `01` §5.1 endpoints published | 37 | **38 of 38**, adding `PATCH /api/v1/datasets/{dataset_id}` |
| `FR-DATA-50`, `FR-DATA-51` | unevidenced | evidenced |
| Alembic head | `9e4c7b21fa08` | `82edffbe1dce` |

Every gate command exit 0, captured by a driver writing `EXIT=$?` per command so that no
result was read through a pipe. **1782 passed, 1 xfailed, 0 skipped** — no skip, so the
database tests ran and the backfill-and-promote migration is genuinely exercised rather than
merely present. Final figures taken at load 3.7–8.3, once the sibling slices had finished.

---

## Where the specification was wrong

`FR-DATA-50` named fewer derived fields than the list view actually needs. Three landed,
governed by a paired-field validator so the pair cannot be half-populated. Per
[`CLAUDE.md`](../../CLAUDE.md) §0 the spec was amended with a dated note saying which side was
wrong, rather than the code being trimmed to match a requirement that was short.

## Where the plan was wrong

| Plan said | Repository |
|---|---|
| `Permission.WORKSPACE_ADMIN` | Does not exist. The nearest real member is `Permission.ADMIN_MANAGE_ROLES` |
| A `FORBIDDEN` error code | The code is `PERMISSION_DENIED` |
| Gate `PATCH` on `dataset:write` | Would have refused `FR-DATA-51`'s own Admin arm — `admin` holds no write permission in this model. Gated on `dataset:read` instead |

## The failure that mattered most

Promoting `owner_id` to `NOT NULL` made 26 tests in `backend/tests/test_api_approvals.py`
raise `NotNullViolationError`: two helpers construct a `DatasetRow` directly and had never
supplied an owner.

The tempting repair — a column default — was **refused deliberately**. A default would have
satisfied every one of those 26 tests while making the new constraint impossible to falsify,
and a constraint that cannot fail is not enforcement. [`CLAUDE.md`](../../CLAUDE.md) §13 rule
4 asks that a check be shown to fail on deliberately broken input, which a defaulted column
never can. The helpers now pass an explicit `owner_id`, and the constraint stays falsifiable.

## Skill updated in the same commit

`.claude/skills/fastapi-service` and its README, per [`CLAUDE.md`](../../CLAUDE.md) §12 —
the permission-gating trap above is exactly the kind of non-obvious procedure that section
asks be captured while it is still fresh.

## Not done

`scripts/demo.py` was **not** run end to end. It unconditionally runs `docker compose up` and
binds ports 8000 and 5173, which was forbidden while sibling slices were executing. The seed
half was exercised through the real Job path (exit 0) and `backend/tests/test_demo_guide.py`
passes in the suite, but the browser walk-through at `/demo` is unverified. It is worth a
manual check in a quiet window.

## Landing dependency

This slice's migration `82edffbe1dce` and W32-2's `7c1a9e40b3d2` both parent on
`9e4c7b21fa08`, which is two Alembic heads the moment both land. W32-2 lands first and this
migration is re-parented onto it. Nothing in the repository enforces a single head, so the
collision would otherwise have merged silently.

## Landing, 2026-08-23: the migration was re-parented after W32-2 merged

W32-2 and W32-3 were executed concurrently and each added a migration off the same parent,
`9e4c7b21fa08`. Once W32-2 landed on `main`, `git rebase origin/main` here **succeeded with
no conflict** — git sees two new files in a directory, which is not a conflict — and left the
chain with two heads, `7c1a9e40b3d2` and `82edffbe1dce`. Nothing in the diff looked wrong.

`82edffbe1dce.down_revision` was therefore moved from `9e4c7b21fa08` to `7c1a9e40b3d2`, in
both the docstring's `Revises:` line and the module attribute. Verified through Alembic's own
`ScriptDirectory`: `heads: ['82edffbe1dce']`, walking back
`82edffbe1dce → 7c1a9e40b3d2 → 9e4c7b21fa08`. The two migrations are independent — one adds a
table, the other a column — so the order between them is arbitrary and chaining is safe.

The divergence is now caught rather than remembered: FR-PLAT-57 and its guard test landed
separately (PR #145) for exactly this case, which is why it was looked for here at all.
