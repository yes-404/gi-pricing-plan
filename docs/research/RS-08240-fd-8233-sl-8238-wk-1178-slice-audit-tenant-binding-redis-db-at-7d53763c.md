---
id: RS-8240
family: research
kind: audit
title: SL-8238 (WK-1178) slice audit at 7d53763c — FD-8233, the tenant-binding tests' Redis db follows GIP_REDIS_URL and avoids the gate dbs
status: draft
created: 2026-10-25
owner: auditor
tree: 7d53763c68c2436a82329809fc85f6770c099b0b
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-8238, LG-8239, FD-8233]
---

# RS-8240 — SL-8238 slice audit at 7d53763c

*(Working id 8240, written by `aud-8233`, 2026-10-25 GMT, from `brief-aud-8233-2026-10-25.md` (lead 28). Check 31/32 on this id and on SL 8238, LG 8239 and FD 8233 are expected until the mint. Tree audited: `7d53763c68c2436a82329809fc85f6770c099b0b`, branch `fix/fd-8233-tenant-binding-redis-db`, range `102341aa...7d53763c`. Docs and diff reading only; no test, gate or pytest run — those are owed.)*

**Verdict PROPOSED (the lead's to adopt): NOT-CLEAN, one B-item (B1) on assert (i), plus two notes (N1, N2).** The fix is correct and red-first is real; the gap is that the new test's assert (i) is weaker than the GO's assert (i) and can pass against a wrong fix.

## Question

Does SL 8238 at gate head `7d53763c` do what FD 8233's accepted remedy and the maintainer's GO require: red-first asserts (i) and (ii), a DB-free red→green, a fix limited to the `redis_url` fixture, and a ledger and roadmap row in the template form?

## Method

Scope from the record first, then evidence (CLAUDE.md §13). Sources: `to-lead.md` entries "2026-10-25 18:59:00 GMT" (1) (FD 8233 accepted, remedy) and "2026-10-25 21:06:06 GMT" (4) (the GO), read in the channel file; then `git -C <wt> diff 102341aa 7d53763c` (5 files), `git show` of the red and fix commits, `git merge-base --is-ancestor` for each cited sha, and a read of `backend/tests/conftest.py`, `conftest_db.py` and the test module's imports for the DB-free claim. Worktree `aud-8233` at `7d53763c`.

**Scope (what the record requires):**

- Remedy, 18:59:00 (1): "derive the test's db index from `GIP_REDIS_URL` when set (the gate's own pytest db), else draw from a range no gate or run-small uses (5–10)".
- GO, 21:06:06 (4): "`redis_url()` derives its db from `GIP_REDIS_URL` when set, else draws from 5–10; **red-first test asserts (i) with `GIP_REDIS_URL` set to each slot's url the chosen db equals that url's db, and (ii) with it unset the db ∉ {1,2,3,4,11,12,13}**; DB-free red-then-green of that one file via run-heavy; no other test touched".

**Scope table (the diff `102341aa..7d53763c`):**

| File | Change | Required by |
|---|---|---|
| `backend/tests/test_tenant_binding_redis_db.py` | new, 34 lines (commit `a4531d80`, red) | GO: red-first DB-free file |
| `backend/tests/test_tenant_binding.py` | `redis_url` fixture only, +6/−2 (commit `1a8762d4`, fix) | remedy |
| `docs/ledgers/LG-08239-…-slice-ledger.md` | new, 53 lines | Lean P2 L1: the slice's one paperwork file |
| `docs/roadmap.md` | SL 8238 row, +20 | Lean P2 L1: the `SL-` row |
| `docs/INDEX.md` | +2 (the two new records) | ledger and row ids |

Nothing else is touched ("no other test touched": met — the fix hunk is the fixture alone; the new file imports it).

## Findings

### Fix body, quoted (`1a8762d4`)

```python
@pytest.fixture
def redis_url() -> str:
    """A Redis database index of its own, so a planted marker stays in this test.

    FD 8233: `GIP_REDIS_URL`'s own db when set; else one of 5-10, which no gate (1-4) or
    seat run (11-13) uses.
    """
    return os.environ.get("GIP_REDIS_URL") or f"redis://localhost:6379/{5 + secrets.randbelow(6)}"
```

`os` was already imported (line 12). `5 + randbelow(6)` is 5..10 inclusive. An empty `GIP_REDIS_URL` falls through to the draw, which is the right reading of "unset". The two other uses of the url (`stores.redis_url`, the `GIP_REDIS_URL` env passed to the subprocess at :302 and :327) read the fixture value, so they follow it. The fix matches the remedy.

### Asserts vs (i) and (ii), quoted

```python
_DRAW = redis_url._get_wrapped_function()
_RESERVED = {1, 2, 3, 4, 11, 12, 13}

def test_set_gip_redis_url_db_is_used(monkeypatch):
    monkeypatch.setenv("GIP_REDIS_URL", "redis://localhost:6379/7")
    assert _db(_DRAW()) == 7

def test_unset_gip_redis_url_draws_outside_reserved_dbs(monkeypatch):
    monkeypatch.delenv("GIP_REDIS_URL", raising=False)
    dbs = {_db(_DRAW()) for _ in range(300)}
    assert not dbs & _RESERVED
    assert dbs <= set(range(5, 11))
```

- **(ii) met.** Unset, 300 draws, none in {1,2,3,4,11,12,13} — the GO's set exactly (`_RESERVED`) — and all within 5–10. With 6 equally likely values, the chance a 300-draw set misses one value is about 6·(5/6)^300 ≈ 10^-23, so the second assert is not flaky.
- **(i) NOT fully met — B1.** The GO says "with `GIP_REDIS_URL` set to **each slot's url**". The test sets one url, db 7. Db 7 lies inside the fallback range 5–10, so a wrong fix that ignored `GIP_REDIS_URL` and always drew from 5–10 would pass (i) with probability 1/6 on each run; the test cannot tell "reads the env" from "draws 5–10". It fails the wrong fix only five runs in six. The reserved dbs (1–4 gates, 11–13 seats) are exactly the values on which a wrong fix is distinguishable. The red run at `a4531d80` did fail (i) — against the old `1 + randbelow(15)` draw, which hits 7 with probability 1/15 — but red-first proves the test fails on the old code, not that it rejects the next wrong code.

### Red-first and the ledger's red/green lines

- `a4531d805cde986d18aa64ebb732c79262a869c5` touches only `backend/tests/test_tenant_binding_redis_db.py` (+34); `1a8762d41bd93c00771a5e91d6d4342434efeaf2` touches only `backend/tests/test_tenant_binding.py`. `git merge-base --is-ancestor a4531d80 1a8762d4` rc 0; `--is-ancestor 1a8762d4 7d53763c` rc 0; `--is-ancestor a4531d80 7d53763c` rc 0 (all three reachable from the gate head, per the role file's two-way ledger rule).
- The LG's build log (read in the file, `7d53763c`): RED at `a4531d805cde986d18aa64ebb732c79262a869c5` — both tests named as `FAILED`, "`2 failed, 2 warnings in 0.56s`, rc=1"; GREEN at `1a8762d41bd93c00771a5e91d6d4342434efeaf2` — "`2 passed, 2 warnings in 0.35s`, rc=0". Each line carries sha, summary line and rc. The maintainer's 21:21:38 GMT line accepted the same pair ("Red→green a4531d80 "2 failed" → 1a8762d4 "2 passed" accepted"). **Met.** I did not re-run them (owed; no grant).
- `ruff check` rc 0 on both files at `1a8762d4`; `ruff format --check` residue on `test_tenant_binding.py` :82, :163, :204 (lines the slice did not touch) was accepted by the maintainer at 21:21:38 GMT.

### DB-free, and how I checked

The new test calls the fixture's function and asserts on the returned string; it opens no Redis or Postgres connection. Checked by reading, not by running: (a) the test file's body has no `redis`, `engine`, `database` or `TestClient` use; (b) its one import of substance, `backend.tests.test_tenant_binding`, has module-level imports only (`app.main`, `app.config`, `conftest_db` helpers) and no module-level connection; (c) `backend/tests/conftest.py` autouse fixtures are `_isolate_probes` (clears an in-process registry) and `_leave_no_frozen_objects` (`gc.unfreeze`) — neither touches a store; (d) the session-scoped autouse `_empty_the_database_after_the_session` (`conftest_db.py:408`) runs `asyncio.run(empty_the_database())` inside `try/except Exception` that only warns; with no per-worktree test DB, `test_database_url()` raises its refusal `RuntimeError` ("…does not exist yet. Refused rather than silently falling back") and the teardown warns — the "per-worktree test-database teardown notice" the LG names as the second of the 2 warnings. So the file is DB-free in its tests; its session teardown is a no-op without a test DB and, on a box with one, is what every run does anyway. (An empirical re-run is owed.)

### LG 8239 and the SL 8238 row — form

- LG sections: Scope, Task list, Gate, Audit, Build log all present as `###` under `## Tasks`, plus `## PRs`; front matter `id`, `family`, `status: active`, `owner: executor`, `slice`, `plans: []`, `relates` — matches `docs/_templates/LG.md` and Lean P2 L1 (a'). The Gate and Audit sections are placeholders ("owed", "not yet"); that is correct for a draft before the gate.
- GO quote: the LG quotes the 21:06:06 GMT item (4) as "GO — FD 8233 fix slice on fix/fd-8233-tenant-binding-redis-db from 102341aa: red-first asserts (i) with GIP_REDIS_URL set the db equals the url's, (ii) unset → db ∉ {1,2,3,4,11,12,13}; DB-free red→green via run-heavy; gate in the next free slot". This is a **paraphrase in quotation marks, not verbatim**: the entry says "with `GIP_REDIS_URL` set to each slot's url the chosen db equals that url's db". The paraphrase dropped "each slot's url", which is the clause B1 turns on. → B2.
- Ids: prose uses the space form ("FD 8233:", "Working ids 8238 (SL) and 8239 (LG)", "ledger"), front matter uses the hyphen form. The record title lines (LG `title:` and H1, roadmap row heading and `title:`) carry "SL-8238"/"FD-8233" in the hyphen form, and the roadmap tail line says "ledger LG-8239" — hyphen in prose, not the record's own id. Under the working-id rule these are N1 (prose/title form); I expect audit-docs check 31/32 to report only own working ids, which is allowed (see the block below).
- Roadmap row: `id: SL-8238`, `family: slice`, `status: active`, `created: 2026-10-25`, `owner: lead`, `tree` = base, `phase: P2`, `work: WK-1178`, `relates: [FD-8233, LG-8239]`; body states the defect, the fix, "Test-only; FR-436 unchanged"; the activation line quotes the GO stamp "to-lead 21:06:06 GMT (4)". Placed among the WK-1178 slices. FR-436 (`07-platform.md`: one tenant per deployment, the marker) is a real requirement; the tests carry `@pytest.mark.req("FR-436")`. **Met.**

### Items

- **B1 (assert (i) can pass a wrong fix).** Make (i) parametrised over the reserved dbs the GO means by "each slot's url" — {1, 2, 3, 4, 11, 12, 13}, each `GIP_REDIS_URL=redis://localhost:6379/<n>` → `_db(_DRAW()) == n`. Then a fix that ignores the env fails every case, none of which lies in 5–10. Red at `a4531d80` already fails any such case, and green at `1a8762d4` passes it, so the red/green lines need re-running on the amended pair, not rewriting. A change to the test file moves the head: the lead decides whether it goes in before the gate's END or as a follow-up commit; this audit does not move the head ("the gate confirms, it does not move the head").
- **B2 (GO quote).** The LG's GO quotation should be the entry's words verbatim, including "set to each slot's url … equals that url's db"; fix as a dated appended LG line (the LG is the slice's own file; no merged record is edited).
- **N1.** Title/H1/roadmap-tail hyphen forms of unminted ids (above) — repoint at the mint (the mint step re-points working ids anyway).
- **N2.** `redis_url._get_wrapped_function()` is a private pytest API (pytest ≥ 8.4's `FixtureFunctionDefinition`). It resolves at the green run (`2 passed`), so it works on the pinned pytest today; a pytest upgrade could break it. I could not read the installed pytest here (no `.venv` in this worktree). Not blocking.

### Verdict

**NOT-CLEAN on B1 and B2**, both small: B1 is a test amendment (more parametrised cases, same two functions), B2 a dated LG line. Everything else the GO requires is met: scope limited to the fixture, red-first with ancestry, (ii) exact, red/green lines with sha and rc, DB-free by reading, LG and roadmap row in template form. If the lead accepts the gate head as the code of record and records B1 as a deferred follow-up with an owner (the fix itself is correct, B1 is a test-strength gap), the verdict is the lead's to soften; I do not.

### Owed (no grant for this draft)

Red/green re-run on the amended pair after B1; `ruff check` on the amended test; audit-docs on the final head; the 13 docs-audit tests at the mint; INDEX regeneration at the mint.

## Addendum — delta audit at 680f7e07 (2026-10-25)

Object: `fix/fd-8233-tenant-binding-redis-db` at `680f7e07e2d86a088c781d127a5e7d0a84dbd91f` (tree 23740b01; `git ls-remote origin` agrees), prior audited head 7d53763c. Authority: to-lead "2026-10-25 22:23:20 GMT" (the named exception (a)–(d)) and "2026-10-25 21:05:20 GMT" item (4) (the GO). Read-only: diffs, quotes and the lead's logged runs; no test was re-run by this seat. The 7d53763c audit text above is unedited.

**Delta, condition (c).** `git diff --stat 7d53763c 680f7e07` = `backend/tests/test_tenant_binding_redis_db.py` (5+/3−) and `docs/ledgers/LG-08239-…-slice-ledger.md` (5+/0−): 2 files, 10 insertions, 3 deletions. No other path, no INDEX change.

**B1 — CLOSED.**
- Decorator at `test_tenant_binding_redis_db.py`: `@pytest.mark.parametrize("n", [1, 2, 3, 4, 11, 12, 13])`; assert `assert _db(_DRAW()) == n` after `monkeypatch.setenv("GIP_REDIS_URL", f"redis://localhost:6379/{n}")`. The set is exactly {1,2,3,4,11,12,13}, the (i) clause "each slot's url".
- Fixture at 680f7e07 (`test_tenant_binding.py:49`, unchanged since the audited head; the diff above does not touch it): `os.environ.get("GIP_REDIS_URL") or f"redis://localhost:6379/{5 + secrets.randbelow(6)}"` → 5–10, disjoint from the parametrised set (condition (d)).
- No other assert weakened: the only changed lines of the file are the decorator, the signature, the comment, the `setenv` and the assert of the first test; `test_unset_gip_redis_url_draws_outside_reserved_dbs` (`not dbs & _RESERVED`, `dbs <= set(range(5, 11))`) is untouched.
- Green: lead-run at 680f7e07, `8 passed, 2 warnings in 0.36s` rc 0 (seat's run at 34f870e2: `8 passed, 2 warnings in 0.43s` rc 0).
- Red (condition (a)): lead-run, uncommitted `git restore --source=a4531d80 -- backend/tests/test_tenant_binding.py`, same file → `8 failed, 2 warnings in 0.52s` rc 1; `scratch/fix-8233/red-b1.log` lines 132–139 list all seven `test_set_gip_redis_url_db_is_used[1|2|3|4|11|12|13]` plus the unset test. Failure messages are the right kind (`assert 12 == 1`, `assert 7 == 2`, `assert 8 == 13`: the old draw ignores the URL). Restored, porcelain 0 (lead's line).
- Condition (b): `ruff check` "All checks passed!" rc 0; `ruff format --check` "1 file already formatted" rc 0 (lead-run at 680f7e07).

**B2 — CLOSED.** The appended LG line is dated (`2026-10-25 22:25 GMT`), marks the earlier GO quote "a paraphrase", and quotes the (i) clause: `(i) with `GIP_REDIS_URL` set to each slot's url the chosen db equals that url's db`. Compared with to-lead.md:31030 (the 21:05:20 entry, item (4)) by `grep -F`: identical, 1 hit. It names 21:05:20, not 21:06:06. `git diff 7d53763c 680f7e07 -- docs`: 0 removed lines, so the earlier line is unedited.

**Notes (non-blocking, no change to the verdict).**
- The LG's own RED line says "NOT RUN" (venv refused rc 76); the red proof is the lead's run in the 22:36 entry. The mint should leave the LG's NOT RUN line as filed and cite the lead's run, or append a dated line quoting it.
- `red-b1.log` opens with a run-small banner and ends on the pytest summary: it is not `head=`-first / `rc=`-last (common brief item 37); the sha and rc are in the lead's entry only. A log fix is for the lead.
- N1 stays with the mint; audit-docs and the 13 remain owed at the minted head (not run here: no grant).

**Proposed verdict: CLEAN** at 680f7e07 (exception (a)–(d) met on the evidence above). The lead adopts or amends.
