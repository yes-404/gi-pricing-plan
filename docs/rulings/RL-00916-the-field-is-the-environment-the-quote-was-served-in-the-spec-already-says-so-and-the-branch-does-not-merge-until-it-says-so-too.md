---
id: RL-916
family: ruling
title: the field is the environment the quote was served in, the spec already says so, and the branch does not merge until it says so too
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-w11-4b-trace-environment-ruling.md
---

# WK-671 Task 4B — what `environment` on a sampled scoring trace means, and how it is derived (2026-08-30)

**What this is.** The ruling on the decision point the lead held PR #485 for: Task 4B stamps
each sampled real-time scoring trace with an `environment`, derived as
`min(caller.environments)`, and the audit reported that derivation as demonstrably wrong
rather than merely arbitrary. Four questions were put — what the field means, whether the
branch may merge as it stands, what the correct shape is, and whether multi-environment
Service Accounts need constraining.

**Numbering continues at 44.** Rulings 1–30 are catalogued in
[`RL-00858-03-5-2-s-identical-step-evaluator-names-an-artifact-that-does-not-exist-the-spec-is-wrong-the-code-is-right.md`](RL-00858-03-5-2-s-identical-step-evaluator-names-an-artifact-that-does-not-exist-the-spec-is-wrong-the-code-is-right.md);
31–32 there, 33 in
[`RL-00871-no-8-stands-unamended-and-unexcepted-and-the-test-the-question-proposed-is-the-wrong-one.md`](RL-00871-no-8-stands-unamended-and-unexcepted-and-the-test-the-question-proposed-is-the-wrong-one.md),
34 in
[`RL-00863-sampling-cannot-remedy-either-requirement-and-the-reasons-differ.md`](RL-00863-sampling-cannot-remedy-either-requirement-and-the-reasons-differ.md),
35 in
[`RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md`](RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md),
36 in
[`RL-00917-the-clause-reaches-persistence-and-nfr-499-is-the-defective-one.md`](RL-00917-the-clause-reaches-persistence-and-nfr-499-is-the-defective-one.md),
37 in
[`RL-00915-option-c-the-compiled-bundle-s-blob-key-becomes-part-of-the-version-s-own-metadata.md`](RL-00915-option-c-the-compiled-bundle-s-blob-key-becomes-part-of-the-version-s-own-metadata.md),
38 in
[`RL-00924-option-b-one-computation-taught-to-answer-the-question-it-already-claims-to-answer.md`](RL-00924-option-b-one-computation-taught-to-answer-the-question-it-already-claims-to-answer.md),
39–41 in
[`RL-00921-a-ref-may-not-be-served-from-the-memo-without-a-metadata-read-and-it-does-not-need-to-be-the-content-hash-is-already-in-hand-after-the-first-read-and-is-discarded.md`](RL-00921-a-ref-may-not-be-served-from-the-memo-without-a-metadata-read-and-it-does-not-need-to-be-the-content-hash-is-already-in-hand-after-the-first-read-and-is-discarded.md),
42–43 in
[`RL-00923-the-schema-is-right-and-is-not-rebuilt-it-is-a-published-data-contract-two-modules-read-so-it-moves-out-of-the-docstring-into-03-4-and-it-does-not-go-into-model-schema-for-a-reason-not-a-deferral.md`](RL-00923-the-schema-is-right-and-is-not-rebuilt-it-is-a-published-data-contract-two-modules-read-so-it-moves-out-of-the-docstring-into-03-4-and-it-does-not-go-into-model-schema-for-a-reason-not-a-deferral.md).

**Mints no `FR-`/`NFR-`/`OQ-` id.** FR-259 takes a dated clarification in place — the
shape RL-889 used for FR-255 and RL-890 for FR-259 itself. No other spec is
edited. That amendment is this ruling's disposition and lands in the same commit.

**Read against `origin/main` at `7a18d7b`** and the branch
`feat/w11-4b-trace-sampling-decision` at its single commit `0a65ac7`. The branch is behind
`main` at that point; nothing below turns on the gap.

**Every claim the lead relayed from the audit was checked against the repository before it
was used here, and every one held.** They are restated below with their own citations rather
than credited, so that a reader need not hold the relay.

---

## RL-916 — the field is the environment the quote was served in, the spec already says so, and the branch does not merge until it says so too

**Ruled in four parts, one per question put.**

### 1. The meaning is not a new decision — the specification already fixes it

`environment` on a `ScoringTraceRow` is **the environment the quote was served in**: the
environment whose live Rating Version FR-250 selects, and against which FR-430
scopes the key that was presented. It is not a summary of what the caller was *permitted* to
reach.

Three parts of the suite say this between them, and no fourth reading survives all three:

- [`../specs/00-overview.md`](../specs/00-overview.md)`:261` — the entity map reads
  `Deployment ──< ScoringTrace (sampled) ──< MonitoringAggregate`. **A ScoringTrace's parent
  is a Deployment.**
- FR-268 ([`../specs/03-rating-engine.md`](../specs/03-rating-engine.md)`:194`) —
  *"Deployment is atomic per environment"*. A Deployment therefore names exactly one
  environment, and the parent link above names exactly one for each trace.
- [`RL-00890-d5-fr-258-259-are-not-silent-about-batch-and-no-open-question-is-raised.md`](RL-00890-d5-fr-258-259-are-not-silent-about-batch-and-no-open-question-is-raised.md) RL-888
  — Deployment is WK-674's, so *"the row carries the parent it can resolve — the rating version
  reference, the bundle hash, and the environment as a plain string — gaining the Deployment
  reference in WK-674"*. The string **is** the deferred parent, held in the only form available
  before `Deployment` exists.

So the field's value must be something a WK-674 migration can reconcile to the Deployment that
actually served the quote. `min(caller.environments)` produces a value that is reconcilable
to nothing: for a caller granted more than one environment it names an environment whose
Deployment did not serve the quote.

FR-430 ([`../specs/07-platform.md`](../specs/07-platform.md)`:141`) closes the mechanism
question the same way, from the credential end: *"A `uat` key can never score against
`prod`."* A **key** has one environment; FR-389 (`07:73`) grants an **account** *"named
environments"*, plural. The specification already distinguishes the account's granted scope
from the call's environment, and the served environment is the key's.

**This is `CLAUDE.md` §0's code-versus-spec question, and the code is the wrong side.** The
spec is under-*stated* rather than wrong — the chain above is derivable but was not derived
by either the executor or the auditor, and the value it governs is written into a record
nothing later corrects. Part 4's amendment writes it down.

**The cited precedent does not hold, and this is not a criticism of the executor's care.**
`_environment_for`'s docstring (`backend/src/app/api/score.py:137-152` at `0a65ac7`) cites
RL-880 ([`RL-00881-dp2-fr-257-splits-into-four-limbs-wk-671-delivers-one-defers-two-with-owners-and-does-not-wire-a-gate-that-could-only-refuse-everything.md`](RL-00881-dp2-fr-257-splits-into-four-limbs-wk-671-delivers-one-defers-two-with-owners-and-does-not-wire-a-gate-that-could-only-refuse-everything.md)`:49`) for
*"the target environment of a call [...] already derivable"*. Read to the sentence that
carries the claim: RL-880 is about resolving the **live Rating Version**, and that phrase
appears inside its argument for why option (a) is not cheap — *"the environment **scope**,
not the pointer: a Service Account carries `environments: list[str]` [...] So the target
environment of a call is already derivable; what is missing is which version is live in
it."* It establishes that the **set** is present and defers everything downstream of it to
WK-674. It never reaches a one-element choice, because nothing in Slice 2 needed one. The
auditor's reading is the correct one; the executor's is not, and the ruling text is
unambiguous enough that no amendment to RL-880 is owed.

### 2. It does not merge as it stands — and the reason is not the one the hold was placed for

**The current derivation is wrong, verified end to end:**

| Step | Evidence at the tree named above |
|---|---|
| The stamp is the lexicographically first granted environment | `backend/src/app/api/score.py:153` — `return min(caller.environments) if caller.environments else None`; called at `:358` |
| Every key is minted for the **list-order** first environment, never any other | `backend/src/app/api/service_accounts.py:180` and `:246` — `generate_key(body.environments[0])` / `generate_key(account.environments[0])` |
| The key's own environment is verified and then discarded | `backend/src/app/auth/service.py:212` checks `parsed.environment not in set(account.environments)`; `:224-230` returns an `AuthenticatedIdentity` carrying `environments=frozenset(account.environments)` and not `parsed.environment` |
| Multi-environment accounts are schema-legal | `backend/src/app/api/service_accounts.py:63` — `environments: list[str] = Field(min_length=1)`, no maximum |
| Nothing exercises more than one | every `environments` literal under `backend/tests` is a single-element list (`test_score.py:102,213,265`, `test_score_batch_api.py:72,92,232`, `test_api_service_accounts.py:66,266`, `test_workspace_switch.py:100`, `test_auth_keys.py:162`) |

An account created `["uat", "dev"]` therefore mints keys scoped `uat` and stamps its traces
`dev`. The two derivations do not merely differ in tie-break rule; they disagree, silently,
with no test able to see it.

**The lead's stated reason for the hold — that a wrong value propagates into Task 4C — does
not hold, and I am recording that rather than accepting the help.** 4C's exclusion signal is
null-versus-non-null, not the value: the frozen plan's own Correction 2
([`../plans/PL-00850-wk-671-slice-4-trace-sampling-the-row-plus-blob-store-and-the-retention-floor.md`](../plans/PL-00850-wk-671-slice-4-trace-sampling-the-row-plus-blob-store-and-the-retention-floor.md)`:104-114`)
replaces *"a batch parent"* with *"a **null `environment`**: the real-time path sets it, and
a trace written on request for a `score.batch` Job carries none"*, and the same convention is
written into `ScoringTraceRow`'s docstring. A wrong-but-non-null environment changes nothing
about which rows 4C returns.

**The reason it must not merge is durability.** Nothing in this platform ever corrects a
trace's `environment` after it is written:

- `write_pending_trace` sets it at serve time and `complete_pending_trace` carries the same
  value through the delete-and-reinsert; no code path assigns it a second value.
- Deletion is refused inside the ≥ 13-month preservation floor —
  `TRACE_RETENTION_FLOOR`, `03` §5.1's owned error codes as amended 2026-08-30 by Task 4A, raised only by
  `app.platform.traces.delete_trace`.
- Migration `835988d1de4c:77-79` revokes `UPDATE` on `scoring_traces`, which is the design
  intent even though **F53** ([`../findings/register.md`](../findings/register.md)) correctly
  records that the revocation is untested against the runtime role. The argument here does
  not lean on F53's open half: with or without an enforced grant, there is no code that
  would issue the correcting write.

So a wrong value is not a latent defect that a later patch cleans up. It is a permanent,
retention-locked, uncorrectable entry in the record `05-monitoring.md` consumes and that WK-674
must reconcile to a Deployment. The window between merging and fixing is a window in which
unfixable rows can be written, and creating a multi-environment account is one authorised API
call away today. That asymmetry — a small fix now against an unrepairable record later — is
the whole of the decision. **Latency of the defect is not a reason to ship it when the defect
is written into an immutable store.**

### 3. The shape: carry the call's environment, do not re-derive it from the grant

**Adopt the audit's remedy, with the field named for what it is.** The defect is
conceptual before it is arithmetic: the code asks an authorisation scope (a set of
environments the caller *may* use) to answer a question about one call (which environment it
*is* using). No tie-break over the set can be right, because the answer is not in the set.

The value is already computed and already verified one frame away. `authenticate_api_key`
parses the key's environment, checks it against the granted set, and then drops it. Carry it:

- `AuthenticatedIdentity` (`backend/src/app/auth/service.py:40-56`) gains a keyword-only
  `environment: str | None = None`.
- `Caller` (`backend/src/app/api/deps.py:60-66`) gains `environment: str | None = None`, as
  a defaulted field on the frozen dataclass.
- `authenticate_api_key` (`:224`) sets it from `parsed.environment`. The bearer path (`:116`)
  and the development path (`deps.py:312`) leave it `None`.
- `_select_workspace` (`deps.py:293`) — the **only** site that constructs a `Caller` — passes
  it through.
- `score.py` deletes `_environment_for` and stamps `caller.environment`.

**Blast radius, stated rather than characterised.** `Caller` is constructed in exactly one
place and `AuthenticatedIdentity` in three, all listed above; the new field is optional and
defaulted, so no other construction site and no reader of `Caller.environments` changes.
`Caller.environments` keeps its present meaning and its present use in authorisation — this
adds a field, it does not repurpose one. No route's authorisation behaviour changes, and no
response shape changes. **This is auth surface, and it is a patch, not a slice**: a slice
would be owed if the authorisation decision itself moved, and it does not.

**Why `parsed.environment` is safe to trust here**, given `auth/service.py:210-211`'s own
warning that the key is *"attacker-supplied and its environment field is a label, not an
authorisation"*: it is used **after** `:212` has checked it against the account's grant, and
only as a record of which granted environment was presented. An unverified label is not
carried anywhere.

**It is also right in both worlds.** Today `generate_key(environments[0])` makes
`parsed.environment` equal to the account's list-order-first environment; if key issuance is
later fixed so that other granted environments are reachable, `parsed.environment` remains
the environment of the key actually presented. `min()` agrees with neither.

**The `None` case is an impossible state and must be treated as one, not stamped.** A
`None` environment on a real-time trace would be indistinguishable from Correction 2's batch
marker, which is a correctness defect in 4C's signal rather than a cosmetic gap. It is
unreachable today: `score:execute` is admitted only by
`service_accounts.py:44`'s `ALLOWED_PERMISSIONS`, is held by no builtin role
(`backend/src/app/platform/rbac.py:159`, FR-347), and there is no roles API in
`backend/src/app/api/` through which a custom role could be given it. **Unreachable is not
the same as prevented** — so the sampling path raises rather than writing a real-time row
with no environment. The existing `except Exception` wrapper in `score.py:341` and `:369-376`
already degrades that to "the quote is still served, the failure is logged", which is the
correct outcome: a missing trace is recoverable, a mislabelled permanent one is not.

**Two tests, each stated as a violation that must become impossible:**

1. A Service Account created `["uat", "dev"]`, scoring with its issued key, produces a trace
   row whose `environment` is `uat`. Under `min()` this returns `dev`, so the test
   discriminates the fix from the defect rather than merely passing.
2. A sampled real-time outcome from a caller carrying no environment writes **no** row, and
   the quote is still served `200`.

### 4. Multi-environment Service Accounts are legitimate. Nothing constrains them; the code handles them

**No schema maximum, no validation rule.** A cap of one would contradict the specification in
two places: FR-389 (`07:73`) scopes keys to *"named environments"*, plural, and FR-430
(`07:141`) — *"A `uat` key can never score against `prod`"* — is a check with nothing to do
unless an account can span environments. Narrowing the schema to make part 3's bug
unreachable would be fixing the specification to suit the code, which is the direction
`CLAUDE.md` §0 forbids.

The invariant that *is* owed is the one part 3 installs and part 4's amendment records: a
sampled real-time trace always carries the environment the call was served in, and absence is
reserved for a batch-produced trace.

**One defect found while checking this, deliberately not ruled here.** Because both
`service_accounts.py:180` and `:246` mint keys with `environments[0]`, an account granted
`["uat", "dev"]` can never obtain a `dev` key through the API at all — the second and later
granted environments are unreachable, and FR-430's check cannot fire against any
legitimately issued key. That is a defect in `main`, in key issuance, and it is outside this
decision point: it is not created, worsened or relied upon by PR #485, and part 3's remedy is
correct whether or not it is fixed. **It is reported to the lead for the findings register
with an owner, and is not ruled by this record.**

---

## Disposition

- **`03-rating-engine.md` FR-259 takes a dated clarification in place**, in this
  commit, naming this ruling. No id is minted, no id is renumbered, no open question is
  raised or decided.
- **PR #485 does not merge as it stands.** The remedy in part 3 is applied on the existing
  branch `feat/w11-4b-trace-sampling-decision` by **a fresh executor** — the 4B executor no
  longer exists — as an additional commit, not a new slice and not a new PR. It is a
  defaulted field on two types, one assignment, one deletion and two tests; the branch's
  existing work is sound and is not reopened.
- **The lead merges**, after the gate; this record does not.
- **Task 4C is unblocked and is not changed by this ruling.** Its exclusion signal was always
  null-versus-non-null and stays so.
- **The key-issuance defect in part 4 is handed to the lead** for the findings register,
  unowned by this ruling.
