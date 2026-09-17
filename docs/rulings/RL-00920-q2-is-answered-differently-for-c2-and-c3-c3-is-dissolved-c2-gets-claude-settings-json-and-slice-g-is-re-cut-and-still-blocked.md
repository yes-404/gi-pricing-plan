---
id: RL-920
family: ruling
title: Q2 is answered differently for C2 and C3: C3 is dissolved, C2 gets `.claude/settings.json`, and slice G is re-cut and still blocked
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md
---

## RL-920 — Q2 is answered differently for C2 and C3: C3 is dissolved, C2 gets `.claude/settings.json`, and slice G is re-cut and still blocked

**Ruled.** RFC-895 §7's Q2 asks two things — *"where registration config lives"* **and**
*"whether C2/C3 run as Claude Code hooks, git hooks, or both."* The second half admits
"neither", and for C3 that is the answer.

### 1. Verified first, at `daa6fbe`

| Claim | Verdict |
|---|---|
| no `.claude/settings.json` | **Confirmed** — absent from disk and from `git ls-files .claude/` |
| no `.claude/hooks/` | **Confirmed** — absent from disk and untracked; no tracked hook script anywhere in the repo |
| no git-hook wiring | **Confirmed** — `git config --get core.hooksPath` is unset |
| slice B put check 26 inside `scripts/audit-docs.py` | **Confirmed** — the check's own comment at `scripts/audit-docs.py:548` reads *"Numbered 26, not 25: 25 is claimed by in-flight work, and a check number is permanent"* |
| a settings file is contemplated as committed | **Confirmed, and it is not neutral** — `.gitignore:81` heads the section *"Claude Code local state (skills and settings ARE committed)"* and ignores only `.claude/settings.local.json` (`:82`) |

### 2. The distinction that decides Q2

**An `audit-docs.py` check can verify a state that is written down. A hook is needed only to
intercept an action that leaves no artifact.** Slice B's C4 fell on the first side — the
extract and the markdown are both files, so a check can compare them — which is why putting it
in `audit-docs.py` deleted impact-matrix rows and left Q2 unanswered. C2 and C3 have to be
sorted by the same test, and they land on opposite sides of it.

### 3. C3 (verify-gate hook) is dissolved

C3 mechanises `delivery-process.md` §6 step 4 — *"the full local gate must be green. **Not yet
built as a blocking hook** — today this is an instruction the executor follows"*. **Ruled: it
is not built, in either form, and the row is closed as discharged rather than deferred.**

- **The state it would enforce is already written down and already checked, by a stronger
  checker.** CI runs the full gate on the pushed branch on a clean runner. A local pre-commit
  hook checks a weaker thing (one machine, one venv) at much higher cost — this repository's
  gate is minutes, and `.claude/skills/dev-commands` records that a Python-only "gate" has
  been green here while the frontend was red, which a local hook would reproduce and CI does
  not.
- **A git hook cannot satisfy `CLAUDE.md` §13 in principle.** It is not installed by clone,
  `core.hooksPath` is unset here, and `--no-verify` bypasses it with no trace. An enforcement
  the actor can silently skip is not enforcement, and no broken-input proof can establish
  otherwise — the proof would only show that the hook fires when it is installed and not
  bypassed.
- **The residual gap is named rather than left implied:** a commit that is never pushed runs
  under no gate. Nothing depends on such a commit, because a Slice closes on a clean audit and
  the lead's merge, and both act on a PR.

The core extract already encodes this preference — `"prefer_existing_check":
"ci_is_authoritative_full_gate_for_pushed_branches"` under `guards.parallelism`. C3 would have
built a second, weaker copy of it.

### 4. C2 (retry-cap hook) genuinely needs a hook, and its home is `.claude/settings.json`

C2 increments the counter in artifact B on every replan/fix loop and, on breach of the cap in
artifact A, **blocks the retry and notifies a human** (`delivery-process.md` §7: *"On breach,
the loop pauses and notifies a human instead of retrying again"*). Blocking an agent's next
action is not a state a file records; it is an interception. Nothing in `audit-docs.py` can do
it.

**Ruled: registration lives in a tracked `.claude/settings.json`; the scripts it registers
live under `scripts/`, in the shape Q2 itself proposes.** Three parts to that, each with its
own reason:

- **`.claude/settings.json`, not `.claude/settings.local.json`.** The local file is
  gitignored (`.gitignore:82`), so a rule registered there would not travel to another
  session, another worktree or another clone — and the rule governs every role, not one
  machine. The gitignore's own section heading already states the intended split.
- **Claude Code hooks, not git hooks, and not both.** The actor the cap governs is an agent
  taking a tool action, and `.claude/settings.json` is the only registration point that
  reaches that actor. §3's objections to git hooks apply here unchanged.
- **No `.claude/hooks/` directory.** Q2 names `scripts/audit-docs.py` as the precedent for
  where a mechanical script lives; a second home for the same class of script is a second
  place to look and a second place to go stale, which is the argument RL-903 already made
  against a new skill. Hook scripts go under `scripts/` — a `scripts/hooks/` subdirectory if
  more than one is needed. `.claude/settings.json` holds registration only.

### 5. §13's broken-input proof, for a hook

A hook proven once by hand is *"a check that has never printed a failure"*. RFC-895 §8(c)
already asks for *"a deliberately cap-breaching test loop … blocked by C2 … in a test
harness"*. **This ruling adds one clause: the harness is a repository test that runs in the
gate, not a manual demonstration.** It drives the hook's entry point with a synthetic runtime
state at cap + 1 and asserts both halves of the on-breach rule — the retry is refused **and**
the notification is produced — and it carries a negative control at cap - 1 that must pass
through, so the harness cannot go green by refusing everything. Slice B's own acceptance set
the standard here: a six-mutation proof with a silent negative control.

### 6. Slice G is re-cut, and Q2 being answered does not unblock it

**G becomes C2 alone** (C3 having been dissolved by §3), and **its blocker changes rather than
clearing.** The adoption record has G *"blocked on RFC-895 Q2"*. Q2 is now ruled. **G is still
blocked — on slice E**, because C2 has nothing to increment until artifact B, the runtime state
file, exists, and E is not started. Naming this is the point: a ruling that answers a
question is easily read as unblocking the row it gated, and here it does not.

E and F also inherit the adoption record §5's instruction — whoever runs them *"must either
take [F27(c) and F29] deliberately or record that they left them"*. This ruling takes neither;
C3's dissolution touches the gate's coverage of the *process*, not the coverage those two
findings name.

**The ruling is overridden** if a hook is registered in `.claude/settings.local.json`, if a
`.claude/hooks/` directory appears, if C3 is built in either form, or if C2 lands with its
enforcement demonstrated rather than tested.

---
