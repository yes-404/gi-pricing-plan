---
id: FD-9959
family: finding
title: The stray cd by team seats recurs despite the charter rule (13 recorded instances since 8 Oct), and only a mechanical guard will hold
status: draft
created: 2026-10-10
owner: auditor
tree: fe0b0627590307259ec6d56be7f73115cf245092
corrected_by: []
relates: [WK-1178, RFC-895, FD-1374]
---

# FD-9959 — the stray cd by team seats recurs; the rule is prose, so it needs a mechanism

*Disclosure: drafted under working id 9959; the id is minted in a later batch mint PR. Written without running any check, test or slot (auditor-fd9959's brief).*

## Finding

The charter rule "Never `cd`" (`.claude/roles/auditor.md`, and the same line in every role that runs commands; amended 2026-10-05 by the maintainer after three slips in one day) does not hold. The maintainer's count at the entry "2026-10-10 16:23:12 BST" in `to-lead.md` is **13**, past the threshold the maintainer set at "2026-10-09 11:48:22 BST" ("at ten or more the valve applies and it becomes an FD with a mechanical fix"). That entry says a briefing line alone is not a remedy: it has failed 13 times. This finding is the FD that ruling asks for, with a mechanical remedy proposal.

No instance of the 13 wrote anything outside its worktree, by each seat's own disclosure. The harm that did occur is earlier and is the reason the rule exists: on 2026-09-30 a persisted `cd frontend` made the project's `PreToolUse` hook refuse every later Bash call (twice that day); on 2026-10-05 two teammate sessions were locked the same way ("2026-10-05 16:46:42 BST" and "2026-10-05 15:24:59 BST" in `to-lead.md`); on 2026-09-26 a lead `cd` moved the cwd every later spawn inherited and a harness lock file landed in the tree under gate (memory `a-lead-cd-contaminates-every-later-spawn`).

## Evidence

### The mechanism (read at `origin/main` = `fe0b0627`)

- `.claude/settings.json` registers one `PreToolUse` hook, matcher `Bash`: `"command": "python3 scripts/hooks/retry_cap_hook.py hook"`, with `"if": "Bash(python3 scripts/hooks/retry_cap_hook.py record*)"`. The script path is **relative to the working directory**. `.claude/settings.local.json` holds only `"permissions": {"deny": []}`.
- After any `cd` out of the repository root, `python3` cannot open that relative path and exits 2, which is the blocking exit code for a `PreToolUse` hook. The maintainer measured it: `cd /tmp && python3 scripts/hooks/retry_cap_hook.py hook` printed "can't open file … [Errno 2]", exit 2 ("2026-10-05 16:46:42 BST" in `to-lead.md`).
- The `if` filter does not save a session: it is evaluated before the hook starts, but matching is best-effort, and a command Claude Code cannot parse statically (pipes, `$(...)`, heredocs, compound forms) runs the hook regardless ("2026-10-05 16:47:09 BST" in `to-lead.md`, citing the hooks reference). So after one `cd`, the next unparseable Bash call is refused, and so is the `cd` that would undo it. The only way out was the user typing `! cd <root>` (memory `never-cd-into-a-subdir-the-hook-path-is-relative`).
- The planned root-cause fix exists and is unbuilt: PL 9617 (working id, branch `origin/pl-9617-hook-abs-path` @ `d862c5a6`, not on `main`) with DP-1 (c) `$CLAUDE_PROJECT_DIR` plus a `git rev-parse --show-toplevel` fallback and DP-2 (a), both accepted at "2026-10-05 15:33:57 BST". It sits in the process backlog (row "2026-10-09 10:54:55 BST", "The `PreToolUse` retry-cap hook is registered by a path relative to the working directory…"). `settings.json` on `main` is still relative.
- Absolute path alone removes the lock-out. It does not remove the habit: a `cd` still moves the cwd that later spawns inherit (the 26 Sep failure), and a seat still ends up running git writes from the wrong tree.

### The instances (every one read in its source; stamps are BST from the record)

Source for the numbered rows: the process-backlog rows "2026-10-09 10:54:55 BST" and "2026-10-10 06:14:11 BST" on `main`, checked against the entries named in the last column. "Disclosed" is the stamp of the entry that records it, not of the command, unless the record gives the command time.

| # | Seat | When | Command shape | Written outside its worktree | Source |
|---|---|---|---|---|---|
| 1 | planner-rfc9479 | 8 Oct, reported "16:04:19" | `cd /dev/null`, failed | nothing | `to-lead.md` "2026-10-08 16:04:19 BST — Status noted (39 open)…" |
| 2 | finisher-sl1448 | 8 Oct, reported "16:04:19" | `cd /tmp` inside a log fetch | nothing | same |
| 3 | minter-g2a | 8 Oct, disclosed 15:47:39 | one `cd /` | nothing ("cwd reset, nothing written") | `from-lead-2026-10-08.md` "2026-10-08 15:47:39 BST" |
| 4 | executor-s2b | 8 Oct, disclosed 14:37:29 | one `cd /tmp`, before any git write | nothing ("shell reset; nothing affected") | `from-lead-2026-10-08.md` "2026-10-08 14:37:29 BST" |
| 5 | minter-s2 | 8 Oct, disclosed 16:56:32 | three bare `cd` | no git write after | `from-lead-2026-10-08.md` "2026-10-08 16:56:32 BST"; `eta.md` cd-slip PATTERN bullet |
| 6 | auditor-branches | 8 Oct, ruled 17:05:15 | `cd /home/puzhenhao1989`, read-only | nothing | `to-lead.md` "2026-10-08 17:05:15 BST" ("Slip #6 (cd)") |
| 7 | minter-d1 | 9 Oct, `eta.md` 10:59:49 | `cd $W` into its own worktree | nothing outside it | `eta.md`; backlog row |
| 8 | executor-s3d | 9 Oct, `eta.md` 11:02:19 | `cd /dev/null`, failed | nothing moved | `eta.md` "SLIP #8" |
| 9 | minter-d3 | 9 Oct, `eta.md` 11:20:00 | `cd $W` inside a grep sweep | no file changed | `eta.md` "SLIP #9" |
| 10 | planner-674s3 | 10 Oct, command at 03:20 | one read-only command beginning `cd /` | nothing; no spawn; cwd unchanged | `eta.md` 03:22:59; backlog row "2026-10-10 06:14:11 BST" |
| 11 | minter-d7 | 10 Oct, `eta.md` 11:53:24 | first Bash call `cd /home/puzhenhao1989` | no git write | `eta.md` 11:53:24; `from-lead-2026-10-09.md` "2026-10-10 13:46:31 BST" (Disclosures) |
| 12 | executor-fd1374g | 10 Oct, `eta.md` 14:45:39 | subshell `cd /dev/null`, failed | no effect | `eta.md` 14:45:39 |
| 13 | planner-remedy-c2 | 10 Oct, entry 16:07:24 | one `cd /tmp/…`, "no-op" | nothing | `from-lead-2026-10-09.md` "2026-10-10 16:07:24 BST" (Disclosures (planner)) |
| ? | planner-remedy-c3 | 10 Oct, entry 16:22:55 | same disclosure text as row 13 | not separately evidenced | `from-lead-2026-10-09.md` "2026-10-10 16:22:55 BST", "Process:" line |

**Reconciliation to the maintainer's 13.** The maintainer's arithmetic is 9 (by 9 Oct 11:48:22) plus 4 on 10 Oct (minter-d7, executor-fd1374g, planner-remedy-c2, planner-remedy-c3). The record gives a different composition with the same total: the nine are rows 1 to 9; row 10 (planner-674s3, also 10 Oct, 03:20) was logged as "the tenth" in the backlog but is not in the maintainer's four; and the 16:22:55 entry lists "planner-remedy-c2/c3" as one planner-side disclosure ("third seat today", naming four seats), so I find one slip evidenced for c2/c3, not two. Rows 1 to 13 are therefore 13 evidenced instances. If c3 slipped separately the count is 14; the record does not show it. The headline (13, past ten) holds either way.

**Instances before 8 Oct, outside the maintainer's series** (found by grep; each read): 3 Oct, one `cd` by the SL-1369 executor (seat not named; "2026-10-03 17:51:16 BST", `to-lead.md`); 5 Oct, planner-rb, planner-9529 (`cd` into its own worktree) and dm-s46 (`cd /tmp`) ("2026-10-05 18:01:45 BST" and "2026-10-05 18:07:10 BST" — the third slip of that day, which produced the charter amendment); 6 Oct, minter-b1 (`cd /tmp/b1`) and minter-chain (`cd /tmp`) ("2026-10-06 01:51:00 BST", `from-lead-2026-10-06.md`). That is 6 more, so 19 evidenced seat slips since 3 Oct, plus the lock-outs and the lead's own 26 Sep and 30 Sep slips above.

**Limit of this evidence.** Every row is a self-disclosure. Nothing detects an undisclosed `cd`, so 13 is a floor. A mechanical guard also fixes this: it can count refusals.

## Remedy — a proposal for the maintainer's ruling

Common facts. A `PreToolUse` hook receives the tool call as JSON on stdin; exit 2 blocks it and the stderr text is shown to the model. `scripts/hooks/retry_cap_hook.py` already models the right failure posture: "a command `hook` cannot confidently parse … is allowed through unparsed — a mis-parse must never falsely block". Tests for that hook live in `tests/test_retry_cap_hook.py`.

### Option (a) — a guard hook alone, registered as the existing hook is (relative path)

A second `PreToolUse` entry, matcher `Bash`, running a new `scripts/hooks/no_cd_hook.py`.
- Catches: a command whose first word, in any simple command, is `cd`, `pushd` or `popd`.
- Misses: everything below, and it is itself a relative-path hook, so one `cd` that reaches the shell by a form it misses leaves the same total lock-out as today.
- Verdict: not enough alone.

### Option (b) — absolute hook paths (PL 9617) plus the guard — **recommended**

1. Both hook commands become cwd-independent: `python3 "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}/scripts/hooks/<hook>.py"`, which is PL 9617's accepted DP-1 (c). Wrap it fail-open: if the file is not found, exit 0, never 2. Reason: DP-2 (a) runs the root checkout's copy in a worktree, the root checkout is pinned to an older branch (memory `the-root-checkout-is-pinned-to-an-old-branch`), and a missing new script must not brick every session. `CLAUDE_PROJECT_DIR` in teammate sessions is undocumented (PL 9617 Task 0 measures it); the fallback fails outside any repository, so the fail-open wrapper is required, not optional.
2. The guard registers with **no `if` filter**. The filter is best-effort and a refusal rule wants to run on every Bash call; the cost is one short Python start per call.
3. Detection, in `no_cd_hook.py`: read `tool_input.command`; drop heredoc bodies; tokenise with `shlex` using `punctuation_chars=True`; split into simple commands at `;`, `&`, `|`, newline, `(`, `)`, `{`, `}`; in each, skip leading `NAME=value` words and the words `builtin`, `command`, `exec`, `time`; refuse if the next word is `cd`, `pushd` or `popd`. Exit 2 with a stderr message naming the replacements (`git -C <path>`, `uv run --directory <path>`, `pnpm --dir <path>`, `env -C <path> <cmd>`, absolute paths). On any internal error or unparseable input: exit 0.
4. Subshells are refused too: `( cd x && cmd )` does not persist, but the charter says "never `cd` in any form" and row 12 was a subshell. A subshell `cd` costs a rewrite to `-C`; refusing it keeps the rule one sentence long. The maintainer may rule the other way (allow `( cd … )`), which removes only the paren case from the split list.
- Catches: every recorded command shape in the table (`cd /`, `cd /tmp`, `cd /dev/null`, `cd $W`, bare `cd`, subshell, `&&`-chained), plus `pushd`/`popd`, `builtin cd`, `command cd`, `FOO=1 cd x`, `if …; then cd x; fi`, `{ cd x; }`, multi-line scripts.
- Misses (stated, not hidden): `source`/`.` of a script that does `cd`, `eval "cd x"`, a variable holding the command word, `bash -c 'cd x; …'` and `python -c 'os.chdir(…)'` (children; the cwd does not persist, so harmless), a `cd` in a spawn made by the harness itself, and a seat editing `.claude/settings.local.json` or setting `disableAllHooks` (the retry-cap hook docstring already concedes this class; the guard stops the habit, not an adversary).
- False positives: `cd` as a first word in code that is not a shell command — mainly lines inside a heredoc body (handled by stripping bodies) and `bash -c` strings (not examined). Words such as `abcd`, `echo cd`, `grep 'cd ' f` and `git commit -m "cd x"` are not first words and pass. A person who really needs a `cd` (the maintainer's recovery `! cd <root>`) uses the `!` shell escape, which I believe does not go through `PreToolUse`; **not measured here**, the red-first probe must confirm it.
- Lives in: `scripts/hooks/no_cd_hook.py` (new), `.claude/settings.json` (both command strings and the new entry), `tests/test_no_cd_hook.py` (new), a skills note in `.claude/skills/dev-commands` replacing the prose caution. Applies to every session in the project, lead and user included, because project settings cannot tell a seat from a lead; the lead's own rule is the same.
- Proof on deliberately broken input, in the style of `tests/test_retry_cap_hook.py`: (i) run the real script as a subprocess, with the subprocess `cwd=` set to `/tmp` and to `docs/` (no shell `cd` anywhere), feeding fixture JSON — red first, against `main`'s relative registration, to show the lock-out; (ii) a refuse table of at least 25 command strings built from the recorded shapes plus the variants above, each asserted exit 2; (iii) an allow table of at least 15 near-misses (`git -C x status`, `uv run --directory x pytest`, `pnpm --dir frontend test`, `env -C x ls`, `echo cd x`, `grep -n 'cd ' f`, `git commit -m "cd x"`, `abcd x`, a heredoc whose body has a line `cd x`), each asserted exit 0; (iv) malformed JSON, empty command and a missing script file each exit 0; (v) a positive control that deletes the refusal branch and confirms (ii) fails, so the table is shown to bite; (vi) a registration test that reads `.claude/settings.json` and asserts every hook command string is absolute or `$CLAUDE_PROJECT_DIR`-anchored.

### Option (b0) — PL 9617 alone (absolute path, no guard)

Removes the total lock-out, the worst consequence. It leaves the habit, the spawn-cwd contamination (26 Sep) and the cwd confusion in git writes. It is already ruled and unbuilt. Keep it as the fallback if the maintainer declines the guard; it is also the first half of (b), so it is not wasted.

### Option (c) — a brief template or checklist line only — **rejected**

The no-`cd` line has been the first checklist item since 8 Oct and a charter rule since 5 Oct; 13 slips followed. The maintainer has ruled that a briefing line is not a remedy.

### Recommendation

Option (b), as one slice under WK-1178 that absorbs PL 9617 (it already carries the ruled DP-1 and DP-2) and adds the guard, with the (i)–(vi) proof above. For the maintainer's ruling: (1) refuse subshell `cd` too (recommended yes); (2) no `if` filter on the guard (recommended yes); (3) fail-open wrapper (recommended yes). Not measured by this audit, to be settled by PL 9617's Task 0 and the red-first probe: whether `CLAUDE_PROJECT_DIR` is set in teammate sessions, and whether `!` bypasses the hook.

## Disposition

Register decision: **fix before close with an owner**. Owner of the finding: the lead's process (WK-1178 carries the hook limb through PL 9617). Severity proposed MEDIUM: none of the 13 caused harm, but the rule fails at a steady rate, the failure it guards against has already locked sessions and failed a gate, and a prose rule has been shown not to hold. Event that next confirms or discharges it: the merge of the slice that registers the guard and the absolute-path hook commands, or the maintainer ruling out the guard, which would leave the finding with option (b0) as its discharge. The lead gives the verdict.
