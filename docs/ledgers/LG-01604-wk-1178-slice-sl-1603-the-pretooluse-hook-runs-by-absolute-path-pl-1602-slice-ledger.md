---
id: LG-1604
family: ledger
title: WK-1178 slice SL-1603 — the PreToolUse hook runs by absolute path (PL-1602, FD-1598's root-cause fix)
status: closed                 # active → closed (§1.2a)
created: 2026-10-10
owner: executor
tree: 10160a3dab254208c8acbf2d274ce639dd4defed
phase: P2
work: WK-1178
slice: SL-1603
plans: [PL-1602]
corrected_by: []
relates: [RL-920, RL-1263, RL-1445]
---

# LG-1604 — WK-1178 slice SL-1603, the PreToolUse hook runs by absolute path

Executed from PL-1602 (minted from working id 9617) by `executor-pl9617`. Working ids: plan 9617,
slice 9618, minted PL-1602, SL-1603 and LG-1604. Stamps are UTC unless marked.

**GO:** `to-lead.md` "2026-10-10 16:40:33 BST — DISPATCH GO: PL 9617 / SL 9618 (absolute hook path, @10160a3d, ≈0.5 lane-day), effective at the FD-1374 slice's merge read-back, minted in D8b. DP-3 and DP-4 as recommended; NO fast-forward of the root checkout". The FD-1374 slice merged as main `e4753e47` (18:07:32 BST).
**MERGE-ACK:** added at merge.

## Tasks

### Scope

The slice's row is `SL 9618 (working id) — WK-1178 slice — the PreToolUse hook runs by absolute path, so a changed working directory cannot block every Bash call` in `docs/roadmap.md`. No FR-/NFR- id. DP-1 (c), DP-2 (a), DP-3 (a) shell form, DP-4 (a) fail-closed.

### Task list

- Task 0 — probes and the red-first proof (below).
- Task 1 — `tests/test_hook_registration.py`, red first.
- Task 2 — `.claude/settings.json` command, DP-3 (a).
- Task 3 — live seat proof (i).
- Task 4 — one gate slot (skill loop, `conftest.py`, `tests/test_root_conftest.py`, one commit).
- Task 5 — skill reason clauses, the gate, closing acts.

### Gate

Full two-half gate, one gate-1 slot (17:13:03 to 18:04:41 UTC), at head `e3c87055` (tree `2b83ed43`), before the id mint:

| stage | rc |
|---|---|
| ruff, mypy, import-linter, req-coverage, contracts --check | 0 |
| frontend install, generate:api, lint, type-check, test, build | 0 |
| audit-docs | 1 (14: unminted ids, check 37 missing `## PRs`, stale INDEX) |
| pytest | 1 (15 failed, 5395 passed; all audit-docs-on-the-real-tree tests) |

Reclassified by the lead (accepted): the reds are the id gap. After the mint and the merge of main `bf457938`, audit-docs and the docs-suite files were re-run on gate-2 (Build log, last entry). The post-gate delta is docs only plus the merge.

### Audit

Written by the auditor.

### Build log

**2026-10-10 17:09 UTC — Task 0, probes (all in a throwaway worktree `probe-9618` on `origin/main` `e4753e47`, run as a child process by `env -C`; never in the executor's own seat).**

- Red, command level (Acceptance 5r, part): `env -u CLAUDE_PROJECT_DIR -C <probe>/docs sh -c 'python3 scripts/hooks/retry_cap_hook.py hook < payload'` → rc=2, stderr `python3: can't open file '<probe>/docs/scripts/hooks/retry_cap_hook.py': [Errno 2] No such file or directory`.
- Red, live (Acceptance 5r), `claude --version` 2.1.296, `claude -p --permission-mode bypassPermissions` started in the probe worktree with `main`'s settings and a scratch logging hook in the probe's own `.claude/settings.local.json`: call 1 `cd docs` ran; call 2 `echo "$(pwd)" | cat` was REFUSED: `PreToolUse:Bash hook error: [python3 scripts/hooks/retry_cap_hook.py hook]: python3: can't open file '…/probe-9618/docs/scripts/hooks/retry_cap_hook.py': [Errno 2] No such file or directory`; call 3 `pwd` ran (parseable, skipped by the `if` filter, as the plan predicts).
- Step 1 (variable in a hook process, top-level session started in a worktree): the scratch hook logged `CPD=<the worktree the session started in>` on all three calls, including after the `cd docs` (pwd=…/docs). So `CLAUDE_PROJECT_DIR` is set and stays at the start directory. DP-2 (a) premise holds for a worktree-started top-level session.
- Steps 2 (teammate and subagent hook processes), 3 (`EnterWorktree` and a teammate spawned in a worktree), 6 (whether a running session re-reads a changed settings file): NOT measured. The executor cannot start a teammate seat. DP-1's fallback is required either way (the plan). For Step 6 the plan's assumption stands: a running session keeps the old command until it restarts.

**2026-10-10 17:10 UTC — Task 1, red (Acceptance 1, 2, 3, 10).** `tests/test_hook_registration.py` at `main`'s settings:
`nice -n 19 uv run pytest -q tests/test_hook_registration.py` → `6 failed, 3 passed`. The five from-docs cases fail with rc 2 and `can't open file '…/docs/scripts/hooks/retry_cap_hook.py'`, including the `deny` case; `test_no_registered_command_names_a_repository_path_relatively` fails on `python3 scripts/hooks/retry_cap_hook.py hook`. The from-root cases (negative control) pass.

**2026-10-10 17:11 UTC — Task 2, green.** Command: `python3 "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"/scripts/hooks/retry_cap_hook.py hook`. `pytest -q tests/test_hook_registration.py tests/test_retry_cap_hook.py` → `20 passed`. The broken-input proof (Acceptance 3) is `test_the_anchoring_check_fails_on_the_old_relative_form`: a scratch settings file with the old command is flagged.

**2026-10-10 17:10 UTC — Task 3, proof (i), green (Acceptance 5).** Throwaway worktree `probe2-9618` (detached at `1bcb46b9`, removed after), `claude --version` 2.1.296, `claude -p` as a child process started there (not the executor's seat): `cd docs` ran; the non-parseable `echo "$(pwd)" | cat` ran and printed `…/probe2-9618/docs`; the `record`-form call `python3 <abs>/scripts/hooks/retry_cap_hook.py record --help` ran and printed its usage; `pwd` printed `…/probe2-9618/docs`. No exit 2, no refusal. The same shape at `main` was refused (Task 0, red). Task 3 Step 2 (a root-started session after the root fast-forward) is the lead's (Hand-off item 6).

**2026-10-10 17:13 UTC — Task 4, red then green (Acceptance 8, 9).** Red, `nice -n 19 uv run pytest -q tests/test_root_conftest.py` at `main`'s skill and `conftest.py` with the two tests changed: `2 failed, 16 passed`. `test_slot_count_matches_the_dev_commands_gate_wrapper`: `assert 2 == 1` with `len(['1', '2'])` the wrapper loop. `test_a_second_bare_run_waits_for_gate_1_and_never_takes_gate_2`: stderr `gate slot …/slots/gate-2 acquired, proceeding`, so `all 2 gate slots are busy` is absent. Green after the skill gate loop, the gate-slot text, and `_SLOT_COUNT = 1`: `18 passed`. Broken-input proof: `_SLOT_COUNT` put back to 2 in a scratch edit → `2 failed, 16 passed` (the same two, same causes); reverted. The skill's `migrate --verify` wrapper and its verify-slot text are untouched.

**2026-10-10 19:08 UTC — merge turn.** `git merge origin/main` (`bf457938`, D8b): conflicts in `docs/INDEX.md` and `docs/roadmap.md` only; the roadmap took main's minted SL-1603 row, the old working-id plan file was removed (main renamed it PL-1602), INDEX regenerated by `scripts/doc-index.py`. No code conflict. On gate-2 at the merged tree: `python3 scripts/audit-docs.py` rc 0 ("All checks passed"); the 8 docs-suite files that held the 15 pytest reds (`test_audit_docs_finding_citations`, `_ids`, `_process_core_digest`, `_w37_11_ceiling`, `test_doc_index`, `test_register_lint`, `test_register_owed`, `test_repository_invariants`): 257 passed (7m14s), so the 15 reds were only the id gap. Targeted: `test_hook_registration.py`, `test_retry_cap_hook.py`, `test_root_conftest.py`: 38 passed. Proofs: (i) Task 3, green; (ii) Task 0, exit 2 red at main; (iii) `test_registered_command_still_denies_a_cap_breaching_record_from_docs` passes, and `git diff --name-only origin/main...HEAD -- scripts/hooks tests/test_retry_cap_hook.py` is empty. Closing acts: LG-1604 and SL-1603 closed, PL-1602 active.

## PRs

The slice PR (number added at open): "SL-1603: the PreToolUse hook runs by absolute path" (merge commit added at merge).
