---
id: FD-1494
family: finding
title: The exit demo's recorded workspace is absent from the database the demo uses, and no check on main verifies that the recorded workspace exists
status: active
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: auditor
tree: 5ff49c6d425f537c7fed19d1212035f18e067b68
corrected_by: []
relates: [WK-1178, SL-1409, PL-1408, RL-1407, FD-1356]
---

# FD-1494 — the demo's `last-seed.json` names a workspace that `gipricing` does not hold

*Disclosure: drafted under working id 9717; minted as FD-1494 on 2026-10-08, in the T2 batch mint PR.*

**Filed** by auditor-fd9717 on the lead's order of 2026-10-05, severity set by the maintainer (by delegation) (2026-10-05 11:57:33 BST,
`to-lead.md`). `tree:` is `origin/main` at filing.
Times below are UTC (BST is UTC+1). **Every query was read-only** (`docker exec gi-pricing-postgres-1 psql -U gipricing
-d gipricing -Atc '<select>'`); nothing was written to any database. SL-1409 Task 7b was migrating and seeding
`gipricing` at the same time, so each figure carries its query time.

## Finding

**Severity MEDIUM** (the maintainer's (by delegation)). **Owner of the remedy: WK-1178.** It does not block SL-1409.

The exit demo reads its login membership from `examples/fremtpl2/data/last-seed.json` (`scripts/demo.py:47`,
`read_seed_record`). That record names a workspace that is not in the database `scripts/demo.py` serves from, and
nothing on `main` checks that the recorded workspace exists, so the gap went unnoticed.

## Evidence

### 1. The recorded workspace is absent

The record (root checkout, gitignored at `.gitignore:61`; read, not touched), mtime `2026-08-27 20:14:44 UTC`:

```json
{"workspace_id": "01a044dc-4e8f-7d58-a39e-1271642267c9",
 "analyst_id":   "01a044dc-4e8f-7b69-8aa5-46ad0aa445da",
 "actuary_id":   "01a044dc-4e8f-78f7-9a76-97638e69da6c"}
```

The database is `scripts/demo.py`'s own: `GIP_DATABASE_URL` defaults to
`postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing` (`scripts/demo.py:190-193`).

| Query (database `gipricing`) | Time (UTC) | Result |
|---|---|---|
| `select count(*) from workspaces where id='01a044dc-4e8f-7d58-a39e-1271642267c9'` | 2026-10-05 10:58:55 | **0** |
| `select count(*) from workspaces` | 10:58:56 | 29 |
| `select id, created_at from workspaces order by created_at limit 3` | 10:58:55 | earliest `2026-09-17 09:59:49.83 +00` (all three on 17 Sep) |
| `select count(*) from users where id='01a044dc-4e8f-7b69-8aa5-46ad0aa445da'` (the analyst) | 10:59:17 | 0 |
| `select count(*) from workspace_members where user_id='01a044dc-4e8f-7b69-8aa5-46ad0aa445da'` | 10:59:18 | 0 |
| `select count(*) from workspace_members where workspace_id='01a044dc-4e8f-7d58-a39e-1271642267c9'` | 10:59:18 | 0 |

The record is 40 days older than the oldest workspace the database holds. Neither the workspace nor the analyst it names exists.

**Alembic revision observed.** `select version_num from alembic_version`: **`c4a81f6d2e95`** at 2026-10-05 10:58:55 and
again at 10:59:13. I did not observe the earlier `d3b955a63d6a`; the lead's relay says the database stood there, behind
the #933 migration, from 2026-09-30 until SL-1409 Task 7b migrated it. By my first query Task 7b had already run
(`max(created_at)` of `workspaces` was `2026-10-05 10:55:58 UTC`, so seeding was under way), so the relay is not
confirmed or refuted by this record.
**Added 2026-10-05 before mint (the before-revision, cited rather than observed).** LG-1417 (SL-1409's ledger, on branch
`sl-1409-validation-rule-approval-through-the-workflow`, unmerged and unminted), in its entry for the Task 7b recovery
(line "B1 — migrate first"), records `uv run alembic upgrade head` at 11:58:44–11:58:46 BST, rc 0, "Revision before
`d3b955a63d6a`, after `c4a81f6d2e95`". That confirms the relay for the before-revision; this record still did not observe
it. LG 9719 (a working id) is LG-1417 now.

### 2. No pre-flight on `main` checks that the recorded workspace exists

`demo()` (`scripts/demo.py:203`) on `main`: `--skip-seed` only skips the seed block (`if not skip_seed:`, `:219`). Then
`read_seed_record()` runs on every path. Its body (`:100-109`) checks that the file exists and that the keys
`workspace_id` and `analyst_id` are present. **It never opens the database.** There is no other pre-flight between that
line and starting the API.

What happens next is incidental, not a check. After the API is up, `_verify_journey_postconditions` (`:297` onward) calls
`/api/v1/models?status=approved` with the recorded analyst and workspace as headers. By `deps.py` `_select_workspace`
(`backend/src/app/api/deps.py`, the `if not identity.workspaces:` branch) a principal with no membership gets
`403 UNAUTHENTICATED "No workspace access"`. `urllib.request.urlopen` raises `HTTPError` on a 403. `main` (`:346-355`, the `except` clauses of `main`)
catches only `DemoRefusedError` and `KeyboardInterrupt`, so that `HTTPError` would end the command as a traceback, after
the API had started, and would name neither the record nor the missing workspace. **This last step is derived by reading
the code; I did not run `scripts/demo.py --skip-seed`.** (A run that does not pass `--skip-seed` rewrites the record
first, so the gap bites the `--skip-seed` path.)

### 3. SL-1409 Task 7a's pre-flight: it refuses, by accident of its zero branch, with a message that names the wrong cause

Read at branch `sl-1409-validation-rule-approval-through-the-workflow` @ `df301c18d354d446606be11ed2b3251d37422560`.
`scripts/demo.py` (`:240-243` at that commit, the `run(` call) runs `scripts/check-rule-sets-runnable.py <record workspace_id>` right
after `read_seed_record()`, on every path. The script's `check` selects the datasets in the workspace that have a rule
set, calls `rule_service.rule_set_to_run` on each, counts the runnable ones, and **if the count is 0 prints
`Workspace <id> has no rule set: the seed did not finish. Re-run the seed.` and returns 1**. It does not check that the
workspace row exists. For an absent workspace the dataset query returns no rows, so it takes the zero branch.

I ran it, read-only, against `gipricing` (not a scratch database: the script opens a session and never a unit of work,
and a scratch database needs a migration to hold the tables, which would test a different path) from the `sl-1409`
worktree, with the recorded workspace:

```
2026-10-05 10:59:12 UTC  uv run python scripts/check-rule-sets-runnable.py 01a044dc-4e8f-7d58-a39e-1271642267c9
Workspace 01a044dc-4e8f-7d58-a39e-1271642267c9 has no rule set: the seed did not finish. Re-run the seed.
exit=1
```

Verdict: **it refuses** (exit 1, not a vacuous `rule sets runnable: 0` pass and not a crash), so the demo no longer reaches
the API with the dead record. But the refusal is a side effect of the "no rule set" guard: it cannot tell "workspace
absent" from "workspace present, no rule set", and its text blames an unfinished seed rather than a stale record. After
its refusal, a `--skip-seed` re-run fails identically, since the remedy is to run without `--skip-seed`, which the text
does not say. The existence check is therefore covered on the branch only incidentally and is not on `main`.

### 4. `ensure_member`'s idempotence claim does not hold for a seed re-run (scope added by the maintainer (by delegation), decision of 2026-10-05 12:00:44 BST)

Read at `origin/main` `5ff49c6d425f537c7fed19d1212035f18e067b68`.

- `backend/src/app/platform/workspaces.py` `ensure_member` (`:48`) states, in its docstring (`:74-76`): "Idempotent ... a seed is re-run against an existing database routinely, and both `uq_workspace_members_user_workspace` and `uq_users_issuer_subject` make a second blind insert an error rather than a no-op."
- Its user lookup is `session.get(UserRow, user_id)` (`:78`): **keyed on the id only**. If no row has that id it adds `UserRow(id=user_id, issuer=issuer, subject=subject)` (`:80`).
- `examples/fremtpl2/seed.py` mints a fresh analyst id on every run, `Principal(... id=new_uuid7() ...)` (`:311`), and passes the same `REALM_ISSUER` and `REALM_SUBJECT` to `ensure_member` (`:359-364`).
- `uq_users_issuer_subject` is `UniqueConstraint("issuer", "subject")` on `users` (`backend/src/app/db/models.py:417`).

So a second seed against a seeded database looks up a new id, finds nothing, and inserts a second `(issuer, subject)` row: a unique violation, not a no-op. The docstring's idempotence holds for the same `user_id`, which a re-run never supplies. **The relay reports SL-1409 Task 7b hit this at 2026-10-05 11:59:10 BST on `gipricing`; I did not observe that failure and did not run the seed. The finding rests on the code above.**

SL-1409 Task 7c works around it in `examples/fremtpl2/seed.py` only (dispatch Delta 17, 2026-10-05 12:01:08 BST): the seed resolves the analyst id from an existing `(REALM_ISSUER, REALM_SUBJECT)` user, else mints one. `ensure_member` and its docstring are untouched by that workaround, so any other caller still meets the mismatch.
**Added 2026-10-05 before mint.** The workaround is commit `d9b069fc8aa6ff820e38a7432cba22abc64d71f2` on branch
`sl-1409-validation-rule-approval-through-the-workflow` (SL-1409 Task 7c). It reuses the realm user's id in
`examples/fremtpl2/seed.py`, so it fixes the seed path only. That branch is unmerged: this record does not claim the
workaround is on `main`.

## Premise recorded by reference (not my ruling)

PL-1408 Task 7 and RL-1407 rely on the recovery "keeps the workspace the demo uses runnable". The lead corrected this
in dispatch Delta 15 (2026-10-05 11:58:25 BST, `DISPATCH-WK-1178-SL1409-2026-10-04.md`, a local handover file, not in the
repository): at 2026-10-05 the recorded workspace was absent, so there was nothing runnable to keep.

## Disposition

**Proposed by the auditor; the lead gives the verdict.**

Owner WK-1178. Make the existence of the recorded workspace and its analyst membership an explicit, named check in
`read_seed_record`'s caller or in the pre-flight, separate from the rule-set count, with a message that names the
record and says to run `scripts/demo.py` without `--skip-seed`; and have `_verify_journey_postconditions` turn an
`HTTPError` into a `DemoRefusedError`. Acceptance: run both paths against a scratch database with the record pointing at
an absent workspace and show the refusal text on each.

**`ensure_member` (evidence 4), options, no pick.** (a) Look the user up by `(issuer, subject)`, and raise a typed error when the found row's id differs from `user_id`, so the id mismatch is refused where it arises. (b) Correct the docstring to say idempotence holds only for a repeated `user_id`. Severity stays MEDIUM. Remedy owner WK-1178.

## State since filing

**2026-10-05, after the filing.** The recorded workspace is no longer absent. SL-1409 Task 7b's recovery seed (12:07:32 BST,
LG-1417) rewrote `last-seed.json`, and the demo record now names a present workspace,
`01a10bbe-3a03-740c-8d4b-a6af38d2dd4b`. The finding stands as the record of the gap: on `main` no check verifies that the
recorded workspace exists, and the pre-flight's refusal for an absent workspace still carries the misleading "the seed
did not finish" message. Severity is unchanged (MEDIUM, the maintainer's (by delegation)).
