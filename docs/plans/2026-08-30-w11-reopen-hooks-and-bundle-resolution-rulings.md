# W11 reopen, NT-0014 Q2, and bundle resolution on the scoring path (2026-08-30)

**What this is.** Three rulings requested by the lead after the maintainer directed that the
uncompleted part of W11 be driven to a real end: how a closed workstream is represented when
work resumes under it, where NT-0014's hook registration lives, and whether a `ref` may be
served from the per-worker memo without a metadata read.

**Numbering continues at 39, 40, 41.** Rulings 1–30 are catalogued in
[`2026-08-29-w11-3-d6-batch-resumability-ruling.md`](2026-08-29-w11-3-d6-batch-resumability-ruling.md);
31–32 there, 33 in
[`2026-08-29-w11-slice-parallelism-ruling.md`](2026-08-29-w11-slice-parallelism-ruling.md),
34 in
[`2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md`](2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md),
35 in
[`2026-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md`](2026-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md),
36 in
[`2026-08-30-w11-nfr-rate-11-quote-input-stores-ruling.md`](2026-08-30-w11-nfr-rate-11-quote-input-stores-ruling.md),
37 in
[`2026-08-30-w11-2b-bundle-resolution-ruling.md`](2026-08-30-w11-2b-bundle-resolution-ruling.md),
38 in
[`2026-08-30-w11-service-account-permissions-ruling.md`](2026-08-30-w11-service-account-permissions-ruling.md).
**Ruling 38 was verified as the highest existing** by searching every `## Ruling N` heading
under `docs/plans/`, not taken from the dispatch.

**Read against `origin/main` at `daa6fbe`**, re-fetched at 2026-08-30T11:22Z immediately
before these rulings were written. `HEAD` of the ruling branch was equal to `origin/main` at
that moment.

**Mints no `FR-`/`NFR-`/`OQ-` id and makes no `docs/specs/` or `docs/contracts/` edit.**
Each ruling states its disposition and who applies it.

---

## 0. One thing the dispatch asserted that this record cannot verify

The dispatch relays that *"the maintainer has now directed that the uncompleted part of W11
be reopened and driven to a real end"*. **No artifact in the tree at `daa6fbe` carries that
direction.** `docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md` §1 quotes three maintainer
messages of 2026-08-30 and §1.1 quotes the delegation; none of them is a reopen instruction,
and §1.1 reads the delegation narrowly — *"It does **not** extend to W11's close, W12, or any
later phase."* The W11 closure record says the same of its own delegation.

So the reopen currently exists only as a relay. `CLAUDE.md` §12: *"Every decision lands as a
dated artifact — a ruling record, an audit record, a plan — never in chat."* **Ruling 39's
first clause is therefore a precondition, not a formality**: the direction is quoted and dated
in an artifact before any of the shape below is applied. This is not scepticism about the
lead; it is the rule NT-0013 exists to enforce, and the lead's own dispatch says to verify
rather than rule against the relay.

---

## Ruling 39 — W11 is reopened under its own id: the closure record is appended to, never amended, and the roadmap's status marker moves while its close note stays verbatim

**Ruled.** Work resumes under **W11**, with the existing slice ids **W11-3** and **W11-4**.
The record takes five parts, in this order. **(ii) below — keeping W11 closed and opening new
rows — is refused.**

### 1. Precondition: the direction is quoted and dated first

Before any edit in parts 2–4, the maintainer's reopen direction is recorded verbatim and
dated, in the same place and the same form the adoption record used for the delegation
(`2026-08-30-nt-0012-0013-0014-adoption.md` §1/§1.1). **The lead records it.** Until it
exists, the reopen rests on a relay and the closure record would be annotated on authority
nobody can find.

**Scope of the reopen, stated because the dispatch bundled two different things.** The reopen
covers **FR-RATE-36, FR-RATE-37 and FR-RATE-42** — and, riding with FR-RATE-42, NFR-RATE-12,
which the closure record §6 tied to it. **Adoption slices E, F and G are not part of it.**
They are a separate Work with its own filed record and its own bounded delegation; folding
them under W11 would put two differently-delegated bodies of work under one id and make the
second close ambiguous about which delegation accepted what. They continue under
`2026-08-30-nt-0012-0013-0014-adoption.md`.

### 2. `docs/audit/work/W11/README.md` §§1–8 are not edited. Not one word

They are the record of what was believed and evidenced at 2026-08-30: the ten FR verdicts,
the NFR verdicts, the measured-and-failing NFR-RATE-1 table in §4, and the §7 plan review.
**A reopen is not a correction.** The close was correct as at its date; the record is not
wrong, and treating the reopen as an amendment would invite a later reader to discount
verdicts that nothing has falsified.

`docs/audit/README.md`'s convention — *"Evidence is write-once. A record that changes after
the fact must say it changed, with the correction dated"* — is satisfied by parts 3 and 4,
which add and date rather than revise.

### 3. One appended, dated section, and one banner line

**`## 9. Reopened <date>`, appended at the end.** Section 9 is minted and never reused
(`CLAUDE.md` §5). It states, and nothing more:

- the direction from part 1, quoted, with its date and who gave it;
- exactly which requirements are back in scope (part 1's list), by id;
- that **§§1–8 are neither corrected nor withdrawn**, and that this section is a change of
  scope rather than a change of belief;
- that §6's *"reassigned — a future batch-scoring slice (36, 37) and a future sampling slice
  (42)"* resolution is **superseded for exactly those rows**, naming them, so §6 read alone
  cannot mislead;
- that the NFR-RATE-1 carry-forward row of §6 — *"owner: an architectural ruling before W14
  deployment"* — is **discharged by Ruling 41 below**, with this record's path.

**And one line under the existing title banner**, where every reader passes:
*"Re-opened in part `<date>` — see §9. §§1–8 are the record as at close and are not
amended."* One line, no verdict touched. This is the minimum that stops a partial read from
misleading, and it is the form the write-once convention explicitly sanctions.

**Who applies it: the auditor writes it, the lead files it.** Closure records at
`docs/audit/work/<id>/README.md` are the auditor's by charter (`.claude/roles/auditor.md`,
Owns). The section carries **no §13 verdict**, so nothing in it is the lead's to issue — but
the lead files it, as §12 has the lead file the record.

### 4. The roadmap row: the marker moves, the close note stays whole

`docs/roadmap.md:376`. **The strike and the ✔ come off the row header. Every word of the
existing close note stays, verbatim.** A dated re-open clause is appended naming the three
FRs, pointing at §9 and at the two filed plans.

**Why the marker moves when `CLAUDE.md` §5 makes things permanent.** §5's permanence is about
**ids and section numbers** — the things a reader navigates by. A ✔ is a **status glyph**, and
status is the one thing the roadmap exists to hold *because* it changes; `CLAUDE.md` §0 puts
status in the roadmap for exactly that reason, and `NT-0003` records four incidents of a
status copy going stale. §13's opening sentence forbids *"a roadmap reporting progress the
repository does not have"*. A ✔ over live work is that defect inverted — it reports completion
of work in flight — and it is the reading a scanner will take.

Keeping the close note verbatim is what preserves the record: nothing is deleted, so the row
still says what was closed, on what evidence, and by whom.

**Who applies it: the lead.** `docs/roadmap.md` is named in `.claude/roles/lead.md` as one of
three paths the lead writes that no other charter claims.

### 5. The re-close is a second, appended close — and the old delegation does not cover it

When the reopened work finishes, `## 10. Second close <date>` is appended. It is audited
under `close-workstream` **against the reopened scope only** — FR-RATE-36, 37, 42, NFR-RATE-12,
and NFR-RATE-1's disposition. It does **not** re-verdict the seven requirements closed on
2026-08-30: re-auditing them would silently replace evidence dated at the close with evidence
dated later, which is the substitution §13's reference rule exists to prevent. If one of them
has since regressed, that is a finding with its own row, not a re-verdict.

**Acceptance of that second close is the maintainer's.** The 2026-08-30 delegation is read
narrowly in two places at once — the adoption record §1.1 (*"covers the landing of NT-0012,
NT-0013 and NT-0014, and nothing else"*) and the closure record's own preamble (*"it covers
this close, not W12 and not any later phase"*). **Neither reaches a second W11 close.** The
lead cannot self-accept it on the delegation already given; a fresh dated line is required.
Naming this now is the point of the ruling: it is the clause most likely to be assumed
inherited.

### 6. Why (ii) — keep W11 closed, open new rows — is refused

It is the cleaner-looking option: no annotation, no moved glyph, every verdict frozen. It is
refused because **it splits one body of work across two ids.** The batch and sampling work
already carries the ids W11-3 and W11-4 in three places — the closure record's §2 slice table,
the filed plan filenames `2026-08-29-w11-3-batch-scoring.md` and
`2026-08-29-w11-4-trace-sampling-persistence.md`, and the rulings those plans cite. A new row
would leave every finding filed against W11 needing re-derivation to a new owner, which is a
failure this project has already had once after a slice re-cut.

`docs/audit/README.md`'s naming convention points the same way: *"A work item is named by its
existing id — a PR number, a slice id, or a workstream id. No new id family is minted here."*

**The ruling is overridden** if the closure record's §§1–8 are edited, if the second close
re-verdicts a requirement closed on 2026-08-30, if a second close is accepted on the
2026-08-30 delegation, or if adoption slices E/F/G are recorded under W11.

---

## Ruling 40 — Q2 is answered differently for C2 and C3: C3 is dissolved, C2 gets `.claude/settings.json`, and slice G is re-cut and still blocked

**Ruled.** NT-0014 §7's Q2 asks two things — *"where registration config lives"* **and**
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
  place to look and a second place to go stale, which is the argument Ruling A2 already made
  against a new skill. Hook scripts go under `scripts/` — a `scripts/hooks/` subdirectory if
  more than one is needed. `.claude/settings.json` holds registration only.

### 5. §13's broken-input proof, for a hook

A hook proven once by hand is *"a check that has never printed a failure"*. NT-0014 §8(c)
already asks for *"a deliberately cap-breaching test loop … blocked by C2 … in a test
harness"*. **This ruling adds one clause: the harness is a repository test that runs in the
gate, not a manual demonstration.** It drives the hook's entry point with a synthetic runtime
state at cap + 1 and asserts both halves of the on-breach rule — the retry is refused **and**
the notification is produced — and it carries a negative control at cap - 1 that must pass
through, so the harness cannot go green by refusing everything. Slice B's own acceptance set
the standard here: a six-mutation proof with a silent negative control.

### 6. Slice G is re-cut, and Q2 being answered does not unblock it

**G becomes C2 alone** (C3 having been dissolved by §3), and **its blocker changes rather than
clearing.** The adoption record has G *"blocked on NT-0014 Q2"*. Q2 is now ruled. **G is still
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

## Ruling 41 — a `ref` may not be served from the memo without a metadata read, and it does not need to be: the content hash is already in hand after the first read, and is discarded

**Ruled.** **No staleness window is admitted, because none is needed.** The question as posed
rests on a premise the code refutes, and with that premise removed the correctness/latency
trade the question assumes does not exist. **NFR-RATE-1 is not amended, and it is not the
defective artifact on the evidence now in hand** — but neither is it shown reachable, and §4
below says exactly what is still open rather than smoothing it.

### 1. Every relayed measurement re-read at source, and each held

Read in `docs/research/w11-task-2d-nfr-rate-1-full-path.md` at `daa6fbe`, not accepted from
the dispatch:

| Relayed | Verdict |
|---|---|
| `_fetch_bundle` alone p99 66.294 ms | **Confirmed**, `:81`, with-GBM, 200 sequential calls, warm slot |
| against a 50 ms whole-request budget | **Confirmed** — `03` §9 `:797`, and NFR-RATE-1 carries **no amendment and no scoping clause**: no "excluding I/O", no warm-cache carve-out |
| over budget at every rung from 10 rps | **Confirmed**, `:128` — *"Every rung is over budget in both conditions"* |
| queue wait p99 7.179 / 4.191 ms at 10 rps | **Confirmed**, `:112` and `:122`; the attribution resolves to fetch, not saturation |
| payload 2,039,114 B | **Confirmed**, `:46` and `:81` |
| the memo is wired to the NFR-RATE-9 branch only | **Confirmed in code** — `slot.hash_for` has exactly one call site in the backend, `backend/src/app/api/score.py:175`, inside `except Exception:` (`:174`). On the happy path the memo is **written** (`:184`) and never read |
| a re-pointed ref would serve a stale bundle | **Confirmed, and it is worse than stated** — see §3 |

Two limits from the measurement's own record, carried forward rather than dropped: **one
pass**, and a **shared 4-core box** with 1-minute load rising to 10.76 during the run. The 200
rps rungs are void by the record's own statement (the generator issued 149.5 and 142.1).

### 2. The premise that does not survive, and what it dissolves

The research note argues the memo cannot move to the happy path because *"the slot is keyed on
`content_hash`, and **the only way to learn a ref's content hash is to fetch the bundle**"*
(`:74-75`). **That universal is false at `daa6fbe`.**

`compile_rating_version` writes the content hash into the version's own row —
`backend/src/app/platform/rating_versions.py:440-444`, `row.bundle = {"content_hash":
bundle.content_hash, "bytes": …, "compiled_at": …}` — and `record_bundle_blob` merges the blob
key into the same dict (`:163`). `_fetch_bundle` reads that dict at
`backend/src/app/api/score.py:126` (`metadata = row.bundle or {}`), takes **only**
`blob_sha256` from it, and **discards `content_hash`**.

So after `_fetch_bundle`'s **first** statement — one indexed `SELECT` on
`(workspace_id, slug, version)`, covered by `uq_rating_versions_slug_version`, deliberately
without `FOR UPDATE` (`rating_versions.py:111-117`) — the content hash is already in hand.
Everything the measurement attributes the cost to happens *after* it: the blob primary-key
lookup (`score.py:135`), the whole-object store read of 2,039,114 B (`:143`), and
`Bundle.model_validate_json` over that payload including the inlined booster text (`:144`).

**Ruled: the authoritative read stays on the hot path and the three dominant terms leave it.**
The version row is read on every request, as now; on a hit against the hash it already
returned, the compiled bundle is served from the slot and the blob read and the 2 MB parse are
skipped. On a miss — which is what a recompiled version produces — the full path runs and
re-hydrates. **Correct by construction, with zero staleness window**, because every request
re-reads the authoritative binding.

This is not a fix instruction and the shape is not mandated beyond the property: *the
resolution's result is used where it is already available, rather than re-derived from the
blob.* How it is arranged, including keeping the ref→hash memo written for §3's benefit, is
the executor's.

### 3. Why the memo route is refused, and a finding that must not land silently

Serving from `hash_for(ref)` without any read is refused, and **not merely because a read is
cheap**. `backend/src/app/platform/bundle_slot.py:28-31` justifies the ref→hash memo on
artifact immutability — *"a given `rating_version` ref names one immutable version and
compiles to one `Bundle` content hash. The mapping cannot change under the memo."*

**That argument is wrong as stated, and the repository already knows it.** `row.bundle` is
mutable: `POST /api/v1/rating-versions/{id}/compile`
(`backend/src/app/api/models.py:1215-1244`) carries no already-compiled refusal, and
`_rating_compile` (`backend/src/app/worker/rating_handlers.py:41-48`) captures `prior_hash`
**precisely because the recompile overwrites it**, then audits `before`/`after` bundle hashes.
The system therefore already models *a changed content hash under an unchanged pinned ref* as
a normal, audited event. A memo-first happy path would serve the pre-recompile bundle under a
window that is not 30 s and not bounded by anything — it lasts until that worker evicts.

It is safe **today** only because `hash_for` is read solely in the degradation branch, where
serving a last-known-good bundle is what NFR-RATE-9 asks for. **The docstring's staleness
argument at `bundle_slot.py:28-31` is a defect in the reasoning, not in the behaviour**, and it
is the sentence a later session would build the happy-path shortcut on. Filing it as a
register row is the auditor's; it is named here so the next reader of that docstring does not
take it as licence.

**A TTL is refused for a second, independent reason.** Workers expire at independent times, so
a TTL produces exactly the *"mixed-bundle requests"* NFR-RATE-6 forbids and the *"never a
mix"* FR-RATE-51 forbids. It is also unprovable under `CLAUDE.md` §13: nothing observes a
window closing, so there is no deliberately broken input that makes a TTL print a failure. A
per-request read is provable — recompile, then assert the next request scores against the new
hash.

**An invalidation signal is refused as premature, and it is already ruled.** Refresh, poll,
pub/sub and an environment pointer are W14's under Ruling 16 clause 4, recorded in
`bundle_slot.py:33-35` — *"A slot that acquires any of them has overridden the ruling."* This
ruling introduces none of them. The push switchover FR-RATE-51 and NFR-RATE-6 describe
(pre-warm, then flip, ≤ 30 s including warming) remains the specified end state and remains
W14's; §2's shape does not conflict with it and does not anticipate it.

### 4. What this does **not** decide — stated plainly, not softened

- **It does not establish that NFR-RATE-1 passes.** It removes the measured dominant term —
  `_fetch_bundle` is 36.574 ms of a 60.959 ms mean handler at the cleanest rung, about 60 %.
  What remains is one `SELECT` plus connection acquisition, `score_one`, and the ~12 ms
  residual of framework, auth, DI and serialisation that NFR-RATE-13 is recorded **owed, not
  delivered** for failing to isolate.
- **The 15 ms limb is the one still in the dock, and it is the requirement's own half.** The
  component re-measure reads p99 **23.027 ms** without GBM against a **15 ms** budget — over,
  *with the fetch already excluded*. The with-GBM component p99 is 33.468 ms, inside 50 ms but
  only 1.49× inside. **If a re-measurement with the blob read removed still fails the 15 ms
  limb, that is the trigger that puts NFR-RATE-1 itself in question**, and answering it from
  today's numbers would be the guess `CLAUDE.md` §0 forbids. The requirement is not amended
  here and the trigger is named so the next decision is a decision rather than a discovery.
- **It does not establish 200 rps.** NFR-RATE-1's budget is *at 200 rps per replica*; the
  measurement never reached it, on a shared box. A re-run needs a dedicated host, and one pass
  will not establish a verdict near a bound.
- **It does not decide the slot's capacity.** `backend/src/app/config.py:172` defaults
  `bundle_slot_capacity` to 1, and its own comment says raising it *"cites a measurement from
  the latency harness"*. With capacity 1 and more than one ref in play the slot thrashes and
  every request pays the full path, so §2's benefit is conditional on a capacity that comment
  requires evidence for. Not set here.
- **A consequence for NFR-RATE-9 that is deferred, not ignored.** Under §2 the metadata read
  stays, so NFR-RATE-9's degradation clause keeps its meaning intact — which is a further
  argument for §2 over the memo route, where the clause would have described the normal path
  and stopped distinguishing anything.

### 5. Disposition — which of code and spec is wrong, and where the change lands

`CLAUDE.md` §0 asks the question and the answer is **the code**, with a narrower defect than
the record it comes from claims. The closure record §5 and the research note both read this as
*"a deliberate correctness choice with an unmeasured cost"* — correctness traded for latency.
**There is no trade.** The value that would buy the latency is read and thrown away four lines
before the expensive work starts. The specification is not overstated and needs no scoping
clause: FR-RATE-24's *"compiled once, distributed, and cached"*, FR-RATE-65's `CompiledBundle`
*"held per worker process"*, and `03` §8's Redis row (*"`Bundle` cache keyed by content hash;
hot-path lookup"*) already describe a hot path that is a cache lookup rather than an
object-store read.

**No `docs/specs/` edit is made or authorised by this ruling**, so `.claude/skills/spec-change`
does not fire and no requirement id moves. The code change is `CLAUDE.md` §0's **first** row —
code inside the current phase — and belongs to the reopened W11 or to whichever slice next
touches the scoring path; the re-measurement belongs with it, since a change made for latency
that is not re-measured is an assertion.

**The W11 closure record §6's carry-forward row** — *"NFR-RATE-1 fails at the full path …
owner: an architectural ruling before W14 deployment. The question is whether a `ref` may be
served from a memo without a metadata read, and what staleness window that admits"* — **is
discharged by this ruling**: the answer is that it may not, and that it does not need to.
Ruling 39 §3 has that recorded in the reopen section.

**The ruling is overridden** if `hash_for(ref)` is read before the version row is read, if a
TTL or an invalidation channel is added to `BundleSlot` before W14, if NFR-RATE-1 is amended
without the re-measurement §4 names, or if the latency change lands without a re-measurement
naming its tree and its host.

---

## Verification

- **Tree:** `daa6fbe`, `origin/main`, re-fetched at 2026-08-30T11:22Z in the same command that
  read the clock, immediately before drafting. Branch head equal to it at that moment.
- **Ruling 38 was established as the highest existing** by enumerating every `## Ruling N`
  heading under `docs/plans/`, not by trusting the dispatch's figure.
- **The absence claims in Ruling 40 §1 were checked two ways each** — on disk and in
  `git ls-files` — because an untracked file on disk and a tracked file absent from disk fail
  differently, and `ls` alone distinguishes neither.
- **Ruling 41's premise refutation was found by reading `compile_rating_version`'s write, not
  by reading `_fetch_bundle` alone.** Reading only the consumer reproduces the research note's
  conclusion; the discarded field is visible only from the producer's side.
- **Every measurement in Ruling 41 §1 was re-read in
  `docs/research/w11-task-2d-nfr-rate-1-full-path.md`**, with its own stated limits (one pass,
  shared box, void 200 rps rungs) carried forward rather than dropped.
- **Ruling 39's charter attributions were read in the role files**, not inferred: closure
  records are the auditor's (`.claude/roles/auditor.md`, Owns) and `docs/roadmap.md` is the
  lead's (`.claude/roles/lead.md`, Tools).
- **§0 records what could not be verified.** The maintainer's reopen direction is a relay with
  no artifact behind it at this tree, and Ruling 39 §1 makes recording it a precondition rather
  than assuming it.
- `python3 scripts/audit-docs.py` — run before commit.
- **Mints no id and registers no error code**, so it owes no [`../open-questions.md`](../open-questions.md)
  mirror row and no [`../roadmap.md`](../roadmap.md) §10 gate row. Makes no `docs/specs/` or
  `docs/contracts/` edit, so it opens no window in which declarations disagree.
