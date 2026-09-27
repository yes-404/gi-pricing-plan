---
id: RL-884
family: ruling
title: M4: the grant is a Service Account, and M4's open half is not open
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slices-2-4-rulings.md
---

## RL-884 — M4: the grant is a Service Account, and M4's open half is not open

**The decision, restated.** M4 records that the frozen map's Task 2.1 instruction to *"grant
`Permission.SCORE_EXECUTE` to the Service Account role (currently granted to none)"* describes a
mechanism that does not exist and would turn a passing test red. It leaves one half unresolved:
whether Slice 2's RBAC test can express *"a scoped Service Account may call it"* before WK-674,
*"and it may prove to be DP1-shaped rather than independent of it."*

**Ruled on both halves. M4's diagnosis is correct; its open half is not open.**

**The diagnosis, verified.** `SCORE_EXECUTE` and `SCORE_BATCH` are `Permission` members
(`packages/model-schema/src/model_schema/permissions.py:58-59`) under a comment that already
says what they are — *"Scoring (`03`, `07`) — the only permissions a Service Account may hold
(FR-347)"* (`:57`). `BUILTIN_ROLES` (`:131`) grants neither, and
`backend/tests/test_rbac.py:101-107`, marked `@pytest.mark.req("FR-347")`, asserts it for
every role slug. FR-347 ([`../specs/06-governance.md`](../specs/06-governance.md)`:83`) is the
requirement. **Task 2.1 grants nothing; it checks `Permission.SCORE_EXECUTE` on the caller.**

**The open half, dissolved by checking the premise.** M4 reasons that FR-347's *"scoped to
named environments"* may make the RBAC test DP1-shaped, because the Environment entity is
FR-428 and WK-674's. It does not, because a Service Account's environment scope is not that
entity and already ships end to end:

- `environments` is a caller-supplied list of strings stored on the row —
  `backend/src/app/api/service_accounts.py:173`, `environments=body.environments`;
- the API key is minted bound to one of them — `:180`,
  `generated = generate_key(body.environments[0])`;
- the key's environment is **enforced at authentication** —
  `backend/src/app/auth/service.py:212`,
  `if parsed.environment not in set(account.environments):`;
- and the authenticated `Caller` carries both scopes — `backend/src/app/api/deps.py:65-66`
  (`environments: frozenset[str]`, `permissions: frozenset[str]`), populated at `:296`.

DP1 turns on **which Rating Version is live in an environment** — a Deployment fact, absent
until WK-674. FR-347 turns on **whether this credential may act in this environment** — an
authorisation fact that has shipped. They share a word and nothing else.

**So Slice 2's RBAC test is writable in full today**, in three cases: a Service Account scoped
to `uat` holding `score:execute` may call the endpoint; the same account without the permission
is refused; and a key for an environment outside the account's list is refused at
authentication, before the route is reached.

**Disposition.** No spec change and no code change beyond Task 2.1's own. The correction is to
the frozen map, which is never edited — this record is its sibling.

**Acceptance test — stated as the violation, and as the predicted failure by cause.** The
violation that must become expressible is the middle case: a Service Account scoped to the right
environment but **without** `score:execute` must be refused by the endpoint. And the standing
guard already exists: **if any commit adds `SCORE_EXECUTE` or `SCORE_BATCH` to a `BUILTIN_ROLES`
entry, `test_rbac.py:101-107` fails naming the offending role slug.** That named assertion is
the expected red for anyone who follows the frozen map's wording. **A different RBAC failure, or
a 403 from an integration test, is not this** — it means something else is wrong, and is a plan
defect rather than the predicted one.

---
