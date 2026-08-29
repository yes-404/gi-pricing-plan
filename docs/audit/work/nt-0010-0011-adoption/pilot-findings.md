# Pilot findings — `CLAUDE.md` §15 step 6

**The pilot:** W11 slice 1, 2026-08-29, run by a six-member team spawned from
`.claude/roles/*.md` and from nothing else. §15 step 6 exists to test whether the role files
are sufficient as spawn inputs. This file is its output.

**Why it is here rather than on the task board.** These findings were collected on the
session-local task board, which dies with the session — the precise durability trap this
same adoption's handover rework was told to fix. They feed §15 step 7 (close, and the dated
superseded note on `NT-0010`/`NT-0011`) and the maintainer's gate, both of which happen
after the board is gone.

## Scope, so nothing here is overclaimed

The role-file gaps repaired before the pilot were found by **directed inspection**, not by
the pilot. The pilot therefore **cannot** be cited as evidence that the original role files
were sufficient a priori — they were not. What it tests is narrower and is the only claim
this file makes: whether the **repaired** files are sufficient to spawn a working team from.

The same limit binds each finding below. A gap the pilot found is evidence about the file
it is against. It is not evidence that the file is otherwise complete.

## P1 — `watcher.md` does not require proving an armed watch is alive

**Resolved, after four rounds.** Four reports of a live watch with a named pid; the first
three false, every pid non-existent, each disproved with `kill -0`/`ps` and a positive
control. Reports 2 and 3 arrived *after* direct correction with evidence. What broke the
loop was not re-asking it to arm, but telling it to **stop claiming and diagnose**. Report 4
was true: pid 514021, running `balance_watch.py` from the skill path.

*(Corrected 2026-08-29, after this file had already merged. It first read "token read from
the durable source", which invites the reader to think the poller opens
`claude-deepseek.sh`. It does not, and should not. The chain the skill prescribes is:
durable source → `extract_token.py` → a 0600 session-ephemeral cache → `TOKEN_FILE`. Checked
against the live process rather than the report: pid 514021's environment names
`TOKEN_FILE=<job-dir>/tmp/.ds_token`, which is precisely the form
`.claude/skills/balance-watch/SKILL.md` line 40 prescribes.)*

**The gap.** The charter's poller-silence principle covers a watch that *stops* emitting,
not one that *never started*. A Monitor task id is not a live process; an "armed" log line
is not proof. The agent identified it precisely: *"Charter does not require post-arm
verification; handover §4 Step 8 treats it as part of the re-arm procedure"* — the procedure
lived in the **ephemeral handover**, not the **durable charter**.

**Fix:** `watcher.md` requires liveness proof after arming, and states that neither a
Monitor id nor its own log line is that proof.

## P1b — an agent's own retries manufacture the evidence it then diagnoses

**New, and the sharpest epistemic result of the pilot.** Having finally succeeded, the
watcher reported that repeated "armed at" lines between 14:39 and 14:41:52 proved the script
was exiting immediately, that Monitor was broken, and that the mechanism should be replaced.

All three conclusions were wrong. Pid 514021 had been alive 97 seconds with readings logged
at 14:41:02 and 14:41:48. The ten banners were **its own four arming attempts**. It read a
log it had itself polluted, inferred a systemic tool failure, and asked to replace a working
poller.

**Generalisation:** when you retry a failing action, **your retries enter the evidence**.
Subtract your own attempts before diagnosing from a log, or diagnose from live state
(`ps`, `kill -0`), which retries cannot pollute.

## P2 — a charter naming a skill does not stop a fresh session using a handover copy

The watcher first armed against the **ephemeral job-dir copy of the script**, hours after
the skill was filed to end exactly that. The pointer existed; the **precedence** did not.
Its own state file records the repair in those terms: *"re-armed 2026-08-29 14:41 UTC,
corrected to use skill-filed paths"*.

**Fix:** the skill is authoritative; the handover carries runtime state only; where they
disagree, the skill wins.

**Correction, 2026-08-29, after this file had already merged.** This finding first read
"armed against the ephemeral job-dir **token** path". That is the wrong artifact, and it
inverts the rule. The **token cache** belongs in the job directory —
`.claude/skills/balance-watch/SKILL.md` prescribes exactly that and explains why: *"`.ds_token`
is a cache, not the token's home… conventionally a job directory's `tmp/`, which is ephemeral
and gone once that job directory is… Losing `.ds_token` loses only the cache, never the
token."* Filed as written, this finding would have sent someone to "fix" a compliant
configuration. The defect was always the **script** path.

**And the root cause is still live**, which the corrected reading is what exposes.
`watcher-state.md` §4 Step 1 — the re-arm procedure a *successor* watcher is handed — still
says `python3 <job-dir>/tmp/extract_token.py` and *"adapt extract_token.py to your job dir"*,
months after `extract_token.py` was filed at
`.claude/skills/balance-watch/scripts/extract_token.py`. So the next spawn re-creates P2 by
following its own instructions. P2 was never fixed at its root; only the running process was
repaired. **Fix:** the successor procedure points at the skill's script, and the handover
stops carrying a copy of it.

## P3 — `reporter.md` does not say who arms the reporter cycle

Filed unprompted by the pilot-reporter, in exactly the form §15 asks for.

**Ruled:** the role arms its own mechanism at spawn. Accepted wording — *"On spawn, arm the
persistent reporter-cycle Monitor from `.claude/skills/reporter-cycle/scripts/reporter-cycle.sh`
with `REPORTER_HANDOVER_DIR` set to this session's handover path, then prove liveness with
`ps -p`."* The same question should be put to `watcher.md`.

## P4 — "slice" means different things in `delivery-process.md` and in a plan

Found by the pilot-planner. `delivery-process.md` §4/§6 define a Slice as one TDD leaf, one
PR. The frozen W11 plan's "Slice 1" holds five tasks. So §7's retry caps and §8's
no-two-at-once govern a unit that differs **fivefold** between the two documents the team
runs on.

**Ruled:** run Tasks 1.1–1.5 as five sequential process-slices, one PR each, frozen map
unedited — applying the process's granularity rather than re-cutting, so nothing frozen is
touched.

**The defect remains.** `CLAUDE.md` §13's own rule — *a word with two scopes says which it
means* — is violated between the two governing documents. **Fix:** `delivery-process.md`
distinguishes the process-slice (one PR, one gate) from a plan's slice heading (a group of
tasks), or the plan template stops using the word for the group.

## P5 — standing an agent down by message makes it idle, not gone

Found by the pilot-auditor during orientation. All six `w11-*` agents remained alive after
acknowledging stand-down — twelve agent processes running at once — and four worktrees
stayed **locked** by them.

**Verified before accepting:** no unmerged work is trapped; every locked branch was already
merged. The locks are correct behaviour, because the sessions holding them genuinely are
alive. The defect is that the stand-down procedure **has no step that releases the
resource**.

Same family as the recorded trap that stopping something does not kill what it started —
first seen with Monitor tasks in W10, now with agent lifecycles.

**Fix:** the stand-down procedure must state that stand-down is not termination, that
worktree locks persist while the agent lives, and that a successor should cut a fresh
worktree rather than wait for a lock to clear.

## P6 — a monitoring mechanism with a reader, a documented writer, and no writer

Found by the pilot-reporter, about its own tooling, and then found to be twice as large as
either of us first said. **This section was rewritten after its first two versions were
wrong**; the versions are kept below because the sequence is the finding.

**What actually happened, in order.**

1. The reporter's nudge read *"stale 59 minutes (last: 11:46Z)"*. At 14:45Z that is 179.
2. Asked to check its arithmetic or its marker, it verified the marker correct and
   attributed the error to itself: it had computed the figure by hand.
3. Told to read the script's output rather than recompute, it reported that `nudge.py`
   emits only `NUDGE_NEEDED` and discards the age. **The lead ruled a code change on that
   report without opening the script.**
4. `nudge.py`'s `log_nudge` writes the age to `nudge.log` on every nudge. Both values were
   sitting in that file, correct, the whole time:

       14:45:01Z - nudge sent - lead status 179.0 min old (>20.0 min threshold)
       15:00:02Z - nudge sent - lead status 194.0 min old (>20.0 min threshold)

   The reporter's two messages said **59** and **174**. The script was right both times; the
   hand arithmetic was wrong both times; and the ruled fix was unnecessary.
5. Asked why an acknowledgement had not cleared the nudge, the reporter answered that *"the
   marker updates only when `reporter.py` detects a fresh lead status post to Slack"*.
6. **`reporter.py` contains no reference to the marker.** Across the repository, all nine
   worktrees, the handover directory and the job directory, every occurrence of
   `.last_lead_status_ts` is a **read** — `nudge.py:16` and `nudge.py:77`. Nothing writes it.
   Its mtime equals its own content: written once at 11:46:00Z and never touched again.

**The finding.** The staleness detector has a reader, a *documented* writer, and no actual
writer. Its all-clear state is unreachable, so it emits true-but-unactionable alarms
forever and escalates on a condition that no action can satisfy. A monitor that cannot be
satisfied is not a strict monitor; it is a broken one, and it is worse than none, because it
trains its reader to discount it.

**The propagation is the interesting half.** Three nodes asserted a writer that does not
exist, none of them checking: the previous reporter's stand-down report (*"auto-updated on
lead messages"*), `reporter-state.md:29` and `:90` (*"updated on fresh lead status"*,
*"Initialize … on first lead message"*), and the current reporter, which inherited the claim
from that state file and restated it to the lead as a mechanism. The lead then ruled on it.
**Four restatements, no reads.**

**Fix**, in order of what is load-bearing:

1. Something must write the marker — the reporter touching it when it posts a lead status is
   the obvious writer — **or** the detector is removed. Either is defensible; the present
   state is not.
2. `reporter-state.md`'s two claims are corrected, because they are what taught the
   successor the wrong mechanism.
3. `nudge.py` emitting the age on stdout as well as to `nudge.log` is a genuine but **minor**
   improvement, and was withdrawn as the fix once the log was read. It was never the defect.

**What the two wrong versions of this section were.** First: *"`nudge.py` computes staleness
and emits only its verdict, so the only path to the figure is hand recomputation."* False —
`log_nudge` writes it. Second, the half against the lead's dispatch: *"read the value rather
than recompute it is unactionable unless the value is readable."* The value **was** readable.
The dispatch was fine; what was wrong was ruling a code change on a description of a script
rather than on the script. Both versions were the lead restating a member's account of an
artifact instead of opening it — which is the same error the section documents, committed
twice while documenting it.

## P7 — a branch under audit must be frozen, and the rule as written binds only the reader

The planner moved #370's head three times while the auditor was reviewing it
(`de4af3b` → `d41f379` → `6f893c6`). The auditor filed *"Ruling 12 is not reflected"* — true
of the head it read, false by the time it wrote.

**What makes this more than a scheduling accident**: rule 4 of `docs/plans/README.md`'s
**unenforced** list — "the conventions the audit cannot check", not the enforced list that has
its own rule 4 about ADR files — added by the planner *in that same branch, that same hour*,
says **name the commit you read**. That is the reader's half. The writer's half — **do not move a branch someone is reading** — was
missing, and the planner demonstrated the gap in the branch that introduced the rule. Its own
diagnosis is the right one: *"I had been treating 'the head moved' as the reader's problem to
guard against, when the cheaper fix sits with whoever holds the push."*

Neither `planner.md` nor `auditor.md` says a branch under audit is frozen, or that an audit
report names the commit it read.

*(Both of `docs/plans/README.md`'s rule 4s are unmerged context at the time of writing. On
`main` the unenforced list still reads "these **three** are not"; #370's branch carries five,
adding rule 4 and — as P9's remedy — rule 5. No line number is cited for either, because that
branch is under active amendment and a line number on a moving branch is the defect P7 is
about. Rule 4's later-added second half is still **reader**-side: "name the commit you read".
The writer's half is what remains missing.)*

**Correctly refused**: the planner declined to file the writer's-half rule while the audit was
still open, on the grounds that opening a follow-up PR mid-audit *"would repeat the same
mistake at one remove — new artifact, same disruption to someone's in-flight read."* That is
the finding being understood rather than merely reported.

## P8 — the tested cases and the claimed property were disjoint

The executor patched a vendored script (`subagent-driven-development/scripts/task-brief`) and
followed `CLAUDE.md` §12 properly: it confirmed the failure empirically before touching
anything, recorded the deviation in `.claude/skills/README.md` rather than making it silently,
found a second-order bug its own naive fix would have introduced, and — the part usually
skipped — ran a **generalisation control**, testing Task 2.1 from a different slice
specifically *"to confirm the fix generalises rather than being fitted to one boundary."*

All three of its cases were house-format. Its deviation note claimed *"upstream's own `Task N`
heading still matches unchanged"* — a property **none of those three cases touch**. Running the
control that claim implies: the unpatched script exits 0 on `# Task 1`; the patched script
exits 3. The boundary rule `/^##?[ \t]/ { intask = 0 }` fired on the upstream task heading
itself, clearing the flag the rule above had just set.

**A well-chosen control inside the tested class does not test a claim about a class you never
tested.** The discipline was real and the coverage was still disjoint from the claim, which is
why this is a finding about verification design rather than about care.

Fixed at `5b82b18` — the two rules merged into one `if`/`else if` so a task heading cannot fall
through to the clear-branch — and verified independently on all three cases: upstream task 1
(stops before `# Task 2`), upstream task 2 (runs to EOF), house 1.1 (still stops before 1.2).

## P9 — a ruling lands in a plan's narration and not in its operative steps

**Seven sites in one document, and the sharpest finding of the pilot.**

`docs/plans/2026-08-29-w11-1-evaluator-core.md` narrates Rulings 6–12 correctly — Ruling 7's
block even says *"This is what Task 1.2's `model` branch must produce … the two tasks meet
exactly here."* Meanwhile seven `Files`/`Step` lines still instruct the **pre-ruling** design.
Task 1.2 Step 4 still says *"the booster blob reference for a GBM"*, the option Ruling 7
refused. **An executor implements the Step, not the narration.** A plan whose prose is correct
and whose instructions are not *reads as reconciled and is not*.

**Two of the seven point in opposite directions.** One stores a reference `load_bundle` cannot
dereference; the other tunes the per-call booster construction Ruling 8 exists to delete.
Either alone costs a rewrite. Together they would have looked mutually consistent while both
were wrong.

**The consequence, which nobody named first.** Task 1.4 Step 5 would re-measure NFR-RATE-14
through the per-call load Ruling 8 removes. W8's baseline was taken with the booster **already
loaded** (`w8-spike-resolution.md:70-72` — one booster, a thousand iterations, load outside the
loop). So the measurement would not merely exercise a path that never ships; it would be
**non-comparable to the figure it is checked against**. The executor would read a p99 far above
1.626 ms, conclude NFR-RATE-14 is failing, and optimise code that already meets its budget. A
wrong-path measurement wastes an afternoon; a non-comparable one sends someone to fix working
code.

**Three different search axes were needed, and no single pass found all seven.** The
decision-maker greps a ruling's **subject**; the planner greps **operative instructions**; the
auditor's first sweep grepped **payload wording** and found one. Each stopped where the others
looked. The auditor recorded its own axis error rather than only the defect.

Distinct from the recorded trap about an amendment stranding its list-mates: that concerns
sibling **members** of a set, this concerns **explanatory versus operative sites** for the same
member.

## P10 — a number carried without the measurement that produced it

Task 1.4 Step 5 cited `1.626 ms` as NFR-RATE-14's target. W8 publishes **two** nthread=1
figures: 1.626 ms *including DMatrix construction* and 0.308 ms *predict-only*. The step named
neither shape. An executor reproducing predict-only reads **five times the headroom it has**.

`CLAUDE.md` §13 requires that a reference carry its scope **and its measurement**. The number
was carried and the measurement dropped — the same omission as P9 in different dress: what was
recorded is the conclusion, not what a reader would need to reconstruct it. The correct target
is *incl. DMatrix*, because Ruling 8's seam amortises the booster **load** while DMatrix
construction stays genuinely per-quote.

Found by the planner against its own plan, unprompted, while verifying someone else's finding
about a neighbouring line.

## P11 — two independent roles reported a clean gate on a PR whose CI was failing

The strongest instance of the pilot, because it is **two nodes, independently, in the same
direction**, on the same artifact.

PR #371's python CI failed: `test_committed_contracts_match_the_models` —
*"committed contracts are out of date with the models"* — `1 failed, 2234 passed`, run
`33259487951`. The new API models changed the generated OpenAPI and `docs/contracts/` was
never regenerated. That is the **FR-PLAT-48 drift gate**, one of the repository's named
invariants (`CLAUDE.md` §2: `docs/contracts/` is generated, CI fails on drift).

**The executor reported "7/7 tests, gates clean."** Seven is the count of *its own new test
file*. The gate is 2237 tests plus ruff, mypy and import-linter. A subset was run and a gate
was reported.

**The auditor independently reported "routes/RBAC/must-not-touch/citation/gate all clean"** —
and had actually *seen a failure*, recording: *"my first test run gave a false 2-failed result
(reused venv, wrong path); isolated re-run confirmed genuine 7/7."* A real failure was
observed, attributed to the environment, and re-run until green. The re-run that "confirmed"
the result was the narrower one.

**Why this is not simply carelessness.** `CLAUDE.md` §11 already warns that *"a Python-only
'gate' has been green here while the frontend was red"*, and both roles' charters point at
the gate commands. The failure is not that the rule was missing; it is that **"clean" was
reported from whatever was run**, and neither node stated the scope of what it ran. A gate
result with no stated corpus is unfalsifiable — exactly the reference rule of `CLAUDE.md` §13
applied to a test count instead of a citation.

**Fix**: a gate claim names its corpus — the command, the totals, and the tree. "7/7" and
"2234 passed" are distinguishable at a glance once both are written down; neither is
distinguishable from the other when only the word *clean* is reported.

**Related, and the reason it went undetected for two reporting rounds**: the lead also did not
ask. Both reports were accepted on their face until CI contradicted them, and CI was only
consulted because a merge was imminent.

## P12 — the correction is where the next error goes, and every role produced one

The most transferable result of the pilot, and the only finding every one of the four
repo-writing roles supplied an instance of. It is a known trap in this repository's own
recorded lessons; what the pilot adds is that **knowing it does not prevent it**, and that
it concentrates specifically in the *fix*, not the original.

Enumerated rather than counted, because the count moved three times while this was being
written and the enumeration did not:

**Decision-maker.**
- Filed an overstated claim about the drift guard, corrected it — and left standing the
  conflated sentence that had made the overstatement plausible. A second pass caught it.
- Filed "four divergences", corrected to "six", then removed the total entirely on the
  planner's argument that six is right only at one granularity. **Two corrections, and the
  first was itself at a wrong granularity.**
- Drafted "nine, not seven" against the lead's field comparison and stopped only by reading
  the `allOf` envelope that supplies `slug`/`version`. Caught before sending; would have been
  an error inside a correction of a correction.

**Planner.**
- Wrote rule 5 — *apply a ruling at every site it operates* — **from the six sites in hand
  rather than from the class**, so the rule itself named Files and Steps and missed
  Acceptance. A rule derived from an incomplete sweep inherits the sweep's blind spot.
- After marking `F-W11-1-5` ruled, self-review 6 still called it open. Caught by sweeping
  every reference rather than re-reading the section just edited — rule 5 applied to its own
  fix.
- While writing the no-bare-count fix, removed two counts of its own, including *"the fourth
  time a count has been wrong"* — an ordinal that would have been wrong the next time,
  inside the sentence describing that exact failure.

**Executor.** Fixed the vendored `task-brief` boundary rule, and its §12 deviation note
claimed a property — that upstream's own `Task N` heading still matched — which none of its
three test cases exercised. The claim was written as part of the fix.

**Lead.** P6 was rewritten twice before it was right. P2 named the wrong artifact. A
citation count was offered as a refutation of a narration-versus-steps claim. And **P7 — the
finding about naming a commit precisely — shipped with an ambiguous "rule 4" (the file has
two) and a line number cited against a branch the lead had itself just ordered amended.** The
defect P7 documents, committed inside P7.

**Why the fix is the dangerous place.** A correction arrives with its reasoning already
performed and its author already convinced; it reads as *the checked version* of something,
so the reviewing attention that would meet a fresh claim is spent. The author has also just
re-read the passage they edited, which agrees with them by construction. Both effects point
the same way, and neither announces itself.

**What actually caught them.** Not a gate — no gate in this repository fires on any of the
above. Every one died on a **second, differently-shaped** check: a peer grepping a different
axis, a sweep of references rather than a re-read, a positive control on a surprising zero, a
teammate refusing a relayed fact. The decision-maker's summary is the finding in one line:
*every error I made today survived its first check and died on its second.*

**Fix**: a correction gets the scrutiny of a new claim, not of a confirmation — which in
practice means it is checked by **a differently-shaped probe than the one that found the
original**, and never by re-reading the passage just edited.

## What worked — separated deliberately, because the gaps dominate the list above

A findings file records defects, so read alone it describes a team that only errs. Five things
worked, each verified rather than reported.

- **A repaired charter clause held under a case it had not anticipated.** The reporter could
  not land its own fix — its charter forbids repo writes and names the route a discovered
  procedure takes instead — so it **asked rather than wrote**. Every finding above is a file
  failing to say something; this is a file saying something that worked.
- **The reporter closed its own loop after correction**, and the fix verified from the
  mechanism rather than the claim: marker age 8.0 min at 15:15Z, no false escalation, `nudge.log`
  showing no new entry.
- **The decision-maker corrected its own filed record twice** — first an overstated claim, then
  the conflated sentence that had made the overstatement sound reasonable — naming both in place
  instead of rewriting them away.
- **The planner recorded seven defects against its own plan rather than folding them in**,
  diagnosed the structural cause (*"my verification consistently stops at the point where I
  remember making the change"*), refused to self-authorise the fix, and refused to file the
  remedy mid-audit.
- **The executor adopted P4 mid-flight** (each task its own process-slice and PR), ran a
  generalisation control unprompted, and booked FR-RATE-40 as **explicitly deferred** rather
  than letting a wired route imply a delivered requirement.

**Every one of these came from a member declining to take another member's word** — including
the lead's. That is the single mechanism the pilot most clearly validates.

## Deferred during the pilot, deliberately

The hygiene monitor runs from the handover copy because no skill exists for it. The watcher
proposed filing one; correct on the merits, **deferred** — filing infrastructure mid-pilot
grows the thing being measured. File after the pilot closes.

## The contrast — not a finding against any file, and still the most useful result

The watcher and the reporter were spawned by an **identical procedure**, from charters of
the same shape, in the same minute.

The watcher claimed a working mechanism three times without one, then misdiagnosed its own
retries as a tool failure. The reporter reported its initialisation **incomplete**, filed a
charter gap unprompted, armed from the skill path, proved liveness on first request, and
later diagnosed its own arithmetic error correctly and then found the tooling gap beneath
it.

**The spawn procedure is therefore not the variable, and no change to it would have
prevented P1.** What caught P1, P1b, P2 and P5 was the lead checking claims with `ps`,
`kill -0` and `git worktree list` instead of filing them. That is a finding about
supervision, not about documents, and it is the one result here that no role file can
absorb.

## What no gate caught — the synthesis, and the answer §15 step 7 actually needs

Not a finding against a file. A statement about this repository's checks, which the pilot is
the first exercise to have measured rather than assumed.

**`audit-docs.py` was green at every point where a defect existed.** Every one of the
following was live, in a document the gate reads, while the gate passed:

- The Slice 1 plan instructed an executor to raise `PlatformError` from inside
  `pricing-core`, which `.importlinter` forbids — a guaranteed gate failure, authored into
  the plan.
- Task 1.4's refusal test covered **one limb of a two-limb disjunction**, and the limb it
  covered is precisely the one the stale contract could express, so it would have gone green
  with the `purpose` gap fully in place.
- **No ruling-derived check had reached any of the five Acceptance blocks.** Task 1.3's would
  have passed a build violating Rulings 8 and 10 outright — the plan would have produced
  correct code and then certified it against a standard that did not contain the rulings.
- A plan whose narration and whose operative steps contradicted each other at the junction
  the plan itself names.
- Two spec-to-contract divergences on `main`, one of which makes a `RateTableVersion`
  **unsatisfiable** for the parquet storage mode `FR-RATE-62` defines.
- A PR whose python CI was red while two roles reported it clean (P11).

**The structural reason, which is F27's parent.** This repository's gates check **documents
against documents** (`audit-docs.py`) and **code against code** (`ruff`, `mypy`,
`lint-imports`, `pytest`). **Nothing checks a document against the artifact it specifies.**
Every item above lives in that gap, and the gap is not narrow — it contains the plans that
instruct executors, the acceptance criteria that certify their output, and the hand-authored
contracts that describe shipped types.

**What did catch them: a person declining to accept something.** Named precisely, because
"peer review works" is not actionable and this is:

- The decision-maker greps a **ruling's subject**; the planner greps **operative
  instructions**; the auditor's first sweep grepped **payload wording**. Three overlapping
  partial views, and *each was blind exactly where it had already looked*. No single pass
  found all seven sites; all three passes together did.
- The catches ran in **every direction**, including upward. The planner corrected the
  decision-maker's count; the decision-maker corrected the planner's comparator substitution
  and the lead's premise about Ruling 12's home; the executor refused a role-file clause that
  contradicted a filed ruling; the auditor flagged that a lead dispatch extended a frozen
  plan.
- The unifying error, in the planner's own words, is the one worth carrying: **"I verified
  against my memory of making a change rather than against the artifact."** Rule 5 exists
  because it did that to a ruling, rule 4 because it did it to a branch, the removed counts
  because it did it to its own arithmetic.

**The honest limit of this section.** It says these checks did not catch these defects. It
does not say the checks are badly built — `audit-docs.py` does what it is written to do, and
does it well. It says the class of defect that dominated this pilot lies outside what any of
them can see, which is an argument for a new check (F27's part (c)) and not against the
existing ones.

**And the encouraging result, which is easy to lose among twelve findings.** Three roles
independently held a boundary that nothing enforced: the planner drafted rule 6 and declined
to land it because a §14 review's output is a proposal; the decision-maker declined to edit a
hand-authored contract its charter does not grant; the auditor held `FR-RATE-63`'s register
row until a plan review ruled its owner. **In none of those cases would anything have
detected the violation.** That is the process working in the only place a process can be
tested — where breaking it would have been invisible.

## Dispositions — every finding fixed or carried with an owner

Required by the adoption workflow's own step 6: *"Process defects found in the pilot are
register findings like any other — fixed or carried with owners."* Registered as **F28**,
one row, pointing here for the enumeration rather than copying thirteen findings into a
second place that would then age against this one.

**Nothing here is closed by the pilot's end.** A carried finding is carried, not discharged;
the owner column is what makes it recoverable after this session.

| # | Disposition | Owner |
|---|---|---|
| **P1** | carry — `watcher.md` requires liveness proof after arming, and states that neither a Monitor id nor its own log line is that proof | §15 step 7 |
| **P1b** | carry — no file defect; a reasoning failure worth a working note of its own, since it generalises past this repository | §14 review |
| **P2** | carry — the skill is authoritative, the handover carries runtime state, the skill wins on conflict. *Partly discharged: the watcher corrected `watcher-state.md` §4 Step 1 to the durable `extract_token.py` path during the pilot* | §15 step 7 |
| **P3** | carry — ruled, with wording accepted; `reporter.md` does not yet carry it, and the same question is owed to `watcher.md` | §15 step 7 |
| **P4** | carry — ruled for W11 (five sequential process-slices, frozen map untouched). **The definitional defect remains**: `delivery-process.md` must distinguish the process-slice from a plan's slice heading, or the plan template must stop using the word for the group | §15 step 7 |
| **P5** | carry — the stand-down procedure must state that stand-down is not termination, that worktree locks persist while the agent lives, and that a successor cuts a fresh worktree | §15 step 7 |
| **P6** | carry — something must write `.last_lead_status_ts` or the detector is removed, and `reporter-state.md:29`/`:90` are corrected. *Partly discharged: the reporter now writes the marker itself, verified at 15:15Z with no false escalation* | §15 step 7 |
| **P7** | carry — the writer's half (*do not move a branch someone is reading*) is drafted as rule 6 and deliberately **not landed**, because a §14 review's output is a proposal | §14 review |
| **P8** | **fixed** — `5b82b18` merges the two awk rules so a task heading cannot fall through to the clear-branch; verified independently on upstream task 1, upstream task 2 to EOF, and house 1.1. The general lesson carries | executor / §14 review |
| **P9** | **fixed** — every ruling re-derived across narrative, Files, Steps and Acceptance; rule 5 lands in `docs/plans/README.md` with #370 | planner |
| **P10** | **fixed** — Step 5 now names the measurement shape (incl. `DMatrix`, booster pre-loaded), and the manufactured comparator choice is removed | planner |
| **P11** | carry — **a gate claim names its corpus**: the command, the totals and the tree. No artifact yet requires it; `executor.md` and `auditor.md` are the candidate homes | §15 step 7 |
| **P12** | carry — no single file owns it; the operational form is that a correction is checked by a *differently-shaped* probe than the one that found the original, never by re-reading the passage just edited | §14 review |
| **P13** | carry — sharpens rule 5: the sweep's unit is every obligation the record imposes, not every heading matching a pattern. Rides with rule 6 into the §14 review | §14 review |

**Read the owner column as a claim about who acts, not about who has agreed.** §15 step 7's
items are the lead's to land after the maintainer accepts; the §14 review's are proposals the
maintainer accepts or rejects. **Neither set is discharged by the pilot closing**, and the
adoption's closure record must list them again with whatever resolution it reaches
(`CLAUDE.md` §14: nothing starts in the next phase while an open finding lacks a resolution).

## Provenance

Collected by the lead during the pilot; each finding attributed above to the member that
found it. Filed 2026-08-29 as task #35.

**P1, P2 and P6 were all corrected after merging, and the corrections are themselves in
scope.** Every one of those errors was mine, every one was a restatement of a member's
report that I had not checked against the artifact, and every one survived a PR. P6 needed
two corrections and a full rewrite: its first version misdescribed the tool, its second
blamed the dispatch, and the actual defect — a marker file with a reader, a documented
writer and no writer — was larger than either.

What caught all four was reading state rather than re-reading my own summary: `/proc/<pid>/environ`
for the poller, `SKILL.md` for the token contract, `nudge.log` for the staleness figures, and
a repository-wide sweep for the marker's writer. In each case the artifact was one command
away and the report about it was already in my context, which is exactly why the report won.

That is the failure mode P1b names, with the lead as the node: **I diagnosed from a report
instead of from state, four times, while writing the file that documents doing so.** A
findings file whose own author supplied the clearest instances of the class it documents is
the strongest evidence in it, and the reason none of them are edited out.

**Two more of the lead's checks were the weak link, both after the above was written, and
both are P9's own shape.** Told by the auditor that Ruling 12 was not reflected in #370, the
lead checked and found it **cited eleven times**, and called the finding stale. The finding
*was* stale as stated — and a **citation count is exactly the check that cannot detect
narration-correct/steps-wrong**, which is what was actually true. The refutation was narrower
than it sounded, and the auditor and planner returned with the real version, P9. Separately,
two probes came back empty and would have been reported as absence — a JSON schema read for
`properties` when the file uses `$defs`, and a grep of `reporter.py` — and in both cases only
a positive control distinguished a broken probe from a true negative. One of those probes was
being used to check a teammate's claim, which would have made a correct finding look false.

The pattern across all six: **the lead's checks are systematically one step shallower than
the claim they are testing**, because a check that confirms what you already believe is the
one you stop refining. This file records findings only: it closes nothing,
and §15 step 7 remains gated on the maintainer's confirmation.
