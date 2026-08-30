# W11 Task 2B — a Service Account's permissions reach no enforcement path (2026-08-30)

**What this is.** The ruling on the blocker `w11-executor-s2a` raised by *running* Task 2B's
tests: a Service Account holding `score:execute` is refused, because the only enforcement path
reads role permissions and a Service Account's are not roles. **12 tests red; Task 2B blocked.**

**Numbering continues at 38.** Rulings 1–30 are catalogued in
[`2026-08-29-w11-3-d6-batch-resumability-ruling.md`](2026-08-29-w11-3-d6-batch-resumability-ruling.md);
31–32 there, 33–36 in the four dated records that follow it, and 37 in
[`2026-08-30-w11-2b-bundle-resolution-ruling.md`](2026-08-30-w11-2b-bundle-resolution-ruling.md).

**Mints no `FR-`/`NFR-`/`OQ-` id and makes no edit.** As with Ruling 37 this is `CLAUDE.md` §0's
first row — FR-GOV-6 already specifies that a Service Account holds these permissions, and
nothing here is a new capability.

**Read against `origin/main` at `0b70a22`.**

---

## Ruling 38 — option (b): one computation, taught to answer the question it already claims to answer

**Ruled: (b), against the recommendation.** The executor recommends (a) — a second dependency
beside `requires` — on the ground that (b) *"widens the effective permission set of every
existing route in one edit"*. **That premise is false, and checking it inverts the answer.**

### 1. The blocker is real and correctly diagnosed

Verified at `0b70a22`: `effective_permissions` (`platform/rbac.py:142-178`) selects from
`RoleAssignmentRow` joined to `RoleRow` and returns only `role.permissions`. A Service Account's
grants arrive by a different route — `auth/service.py:230` sets
`permissions=frozenset(account.permissions)` on the identity, `api/deps.py:297` copies it to
`Caller.permissions` — and nothing reads it. The diagnosis, the fail-closed direction and the
"no route has ever required a Service-Account permission before" explanation all hold.

### 2. The premise that decides the option, checked

(b) was refused because it would widen every route for every principal. **It would not.**

- `AuthenticatedIdentity.permissions` is declared `frozenset[str] = frozenset()`
  (`auth/service.py:51`) and `Caller.permissions` likewise (`api/deps.py:66`).
- `permissions=` is assigned on an identity in **exactly one place** in `auth/service.py` —
  line 230, the Service-Account path. `git grep "permissions=" ` over that module returns that
  single hit.

**So `Caller.permissions` is empty for every user principal.** Unioning an empty set changes
nothing: not enforcement, not the UI, not one existing route. **(b)'s blast radius is Service
Accounts alone, and for them it replaces a wrong answer with a right one.**

### 3. And the docstring the recommendation cites argues the other way

The argument against (b) rests on `effective_permissions` being shared by enforcement and the
frontend. That is true, and it is the reason to choose (b). Its own docstring:

> Every permission the principal holds here, right now.
>
> Used by the API to tell the frontend what to show (FR-GOV-2's second sentence). … **it is the
> same computation the enforcement uses — a second implementation would let the UI offer a
> control the backend then refuses.**

Two things follow.

- **The function is already wrong by its own first line.** For a Service-Account principal it
  does *not* return every permission the principal holds. (b) is not a widening; it is a repair.
- **(a) is the second implementation that docstring exists to forbid.** It would create a
  parallel enforcement path whose answer differs from the one the UI reads — the same defect
  with the sign flipped, the backend permitting what the surface does not show. The executor
  already names the cost from the other side: *"choosing wrong is an authorisation defect rather
  than a bug."* A codebase that deliberately kept one computation should not gain a second
  under time pressure. **(c) is refused for the reason the executor gives.**

### 4. Where the union goes, and the constraint that comes with it

**Inside `effective_permissions`, not at the `requires` layer** — unioning at `has_permission`
would fix enforcement and leave the frontend's answer wrong, recreating §3's divergence rather
than closing it.

**But the authenticated set is passed in, never re-derived.** `effective_permissions` takes a
`Principal`, not a `Caller`, so a naive reading of the paragraph above has it look the account's
grants up by principal id. **That is refused.** A lookup returns what the account row says
*now*; `Caller.permissions` is what the presented credential actually authenticated with. Today
those are equal — `auth/service.py:230` populates the identity straight from the row — but they
are equal by coincidence of the current implementation, not by construction, and the day a
credential carries a subset of its account's grants the re-derivation silently enforces the
larger set. **An authorisation fix must not rest on an invariant nobody states.**

So the signature gains the authenticated set as an explicit parameter — a `frozenset` defaulting
to empty — and the callers that hold a `Caller` pass `caller.permissions`: `api/me.py:112`, the
frontend's own endpoint, and the `has_permission` path beneath `authz.requires`. Every other
caller takes the default and is unchanged, which is the same reason §2's blast radius is nil.

**This keeps what the executor's (a) was protecting.** Their ground for (a) is that it *"keeps
the verified set and the enforced set the same object"* — that property is real and it is what
matters here. It is not exclusive to (a): passing the object achieves it without a second
enforcement path.

**The danger above is prospective, not present, and the record should say so.** Verified at
`0b70a22`: the credential path **rejects rather than narrows**. `auth/service.py:212` raises
`ENVIRONMENT_SCOPE_DENIED` when the key's environment is not among the account's, with the
comment *"the key is attacker-supplied and its environment field is a label, not an
authorisation"*; `:230` then returns `permissions=frozenset(account.permissions)` — the whole
set, unconditionally. **So today `Caller.permissions` equals the account's set exactly, and a
principal-id lookup would lose nothing.** Recorded because it was nearly grounds to block this
ruling, and because a refusal whose danger is prospective should not be written as though the
danger were live.

**No tripwire is attached to that fact, and the reason is §5's limb 2.** One was drafted — *"if
`AuthenticatedIdentity.permissions` ever becomes a narrowed subset, this becomes an
over-grant"* — and it is **withdrawn**, on two grounds of which the second is the one worth
carrying.

- **It has no referent under the ruled design.** A passed set **is** the narrowed set, so
  upstream narrowing correctly narrows what is enforced — right behaviour, not a hazard. And
  re-scoping it to fire on a re-implementation reduces to *"do not revert this ruling"*, which
  every ruling already says.
- **The guarantee it wanted is already mechanised.** §5's limb 2 — *a `Caller` whose
  permissions differ from its account row is enforced on the `Caller`'s* — **is red under any
  lookup re-implementation**, because a lookup has no way to disagree with the row. So the
  hazard is watched by a failing test rather than by a sentence, and **a test fires where prose
  does not.**

That is the better reason, and it generalises past this ruling: **a watch is worth writing only
where no check can be made to fail in its place.** Here one can, so the watch is redundant
rather than merely unfounded.

A companion note observing that `environments` is built the same way in the same constructor is
withdrawn with it. Nothing in this ruling changes `environments`, so there is no list-mate being
stranded — only a speculative parallel whose sole consequent was the withdrawn watch.

The two conditions that *do* reopen this are in the override line below, and both are
observable: a non-Service-Account writer for `Caller.permissions`, which would falsify §2's
blast-radius finding, and a resource-scoped entry in `ALLOWED_PERMISSIONS`, which would
outrun `_covers`.

**The scope constraint, because the two grant kinds do not carry the same thing.** A role
assignment is scoped and filtered by `_covers`; a Service Account's permissions carry no scope.
Unioning them makes them satisfy any `resource`. That is correct **only because**
`api/service_accounts.py:44` restricts them to
`ALLOWED_PERMISSIONS = frozenset({"score:execute", "score:batch"})`, both workspace-level
operations with no resource to scope to. **That restriction is now load-bearing for
authorisation, not merely for tidiness: if a resource-scoped permission is ever added to that
set, `_covers` must be extended in the same change.** It is named in the override condition
below so the next person to widen the set meets it.

### 5. The negative test must be shown to fail before it is trusted

The executor already wrote `test_an_account_without_score_execute_is_refused` and flags that it
**currently passes for the wrong reason** — everything is refused today. That is the whole of
`CLAUDE.md` §13's *"a check that has never printed a failure has not been tested"*.

**And the direction makes green worthless as evidence.** Everything is refused today, so a fix
that grants *too much* turns all twelve red tests green — indistinguishable, on the suite alone,
from a fix that grants exactly right. **A passing gate is not evidence for this change.** Two
limbs are owed, and neither is a suggestion:

1. **The mutation.** With the union in place, granting `score:execute` to the account in
   `test_an_account_without_score_execute_is_refused` must flip it from pass to fail. A test
   that passes before the change, after it, and under the mutation is measuring nothing.
2. **The enforced set is the *authenticated* set.** A `Caller` whose `permissions` differ from
   its account row must be enforced on the `Caller`'s. This is the test that separates the
   ruling's design from the re-derivation §4 refuses — and **it is only expressible because the
   set is passed rather than looked up.** A re-derived implementation cannot be made to fail
   this test, because it has no way to disagree with the row.

That second limb is the point of §4 restated as a check: **the safe design here is the one whose
safety is testable**, and the unsafe one is unsafe precisely because nothing can catch it going
wrong.

### 6. Not decided here

Whether a Service Account should be able to hold permissions *via roles* as well, which would
make the two paths one at the data layer rather than in the computation. That is a governance
question about `06`'s principal model, it is not needed to unblock Task 2B, and the union
ruled above is compatible with it if it is ever taken.

**The ruling is overridden** if `Caller.permissions` acquires a non-Service-Account writer —
which would make §2's blast-radius finding stale and reopen (a) — or if `ALLOWED_PERMISSIONS`
gains a resource-scoped permission without `_covers` being extended in the same change.

---

## Verification

- **Tree:** `0b70a22`, `origin/main`, re-fetched immediately before this was written.
- **The blocker's own three facts were re-read**, not accepted: the `RoleAssignmentRow`/`RoleRow`
  select in `effective_permissions`, the `permissions=frozenset(account.permissions)` assignment,
  and the copy onto `Caller`.
- **The premise that decided the option was checked rather than inherited.** The recommendation
  turns on (b)'s blast radius; the two default declarations and the single assignment site are
  what establish it is empty for users. **Had that not been checked, the recommendation would
  have been adopted** — it is well argued and its conclusion is wrong only because of a fact
  neither the report nor the escalation states.
- **The docstring was read in full rather than cited.** It is quoted in the report as an argument
  *against* (b); reading the whole of it — *"every permission the principal holds"* plus the
  second-implementation warning — is what turned it into the argument *for* (b).
- **The scope interaction was derived from `_covers`**, which the report does not mention, rather
  than assumed to be absent because the reported symptom did not involve it.
- `python3 scripts/audit-docs.py` — run before commit.
- Makes no `docs/specs/` or `docs/contracts/` edit and mints no id, so it owes no
  [`../open-questions.md`](../open-questions.md) mirror row and no
  [`../roadmap.md`](../roadmap.md) §10 gate row.
