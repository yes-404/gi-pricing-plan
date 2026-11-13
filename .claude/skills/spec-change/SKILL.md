---
name: spec-change
description: Add or modify a requirement, section, or open question in the docs/specs/ specification suite of this GI pricing platform. Use whenever adding an FR-/NFR- requirement, editing a module spec (00-overview through 07-platform), raising or resolving an OQ- open question, or changing a spec's data contracts, interfaces, or tech dependencies. Enforces the append-only requirement-ID rule, the ten-section standard, and both-direction cross-referencing. Also carries the four things a spec introducing a custom objective must say (declaration, validation, versioning, audit) before it is complete.
---

# Changing a spec

The specification suite is the product of Phase 0 (`CLAUDE.md` §2). Specs are versioned
prose with **permanent identifiers** — the failure mode is not a typo, it is a broken
traceability chain that nobody notices for months.

## Before editing

1. Read `docs/specs/00-overview.md` §2 (glossary) and §7 (module map) — terminology must
   match exactly. A new term goes in the glossary **before** first use anywhere.
2. Read the target spec end to end. Read any `docs/workflows/` file that references it.

## The rules that are easy to break

**Every JSON example declares what it is, on its fence.** ` ```json schema=<Class>` names a class in
`model_schema.__all__`, and the block must pass `<Class>.model_validate` in full. ` ```json illustrative`
marks a fragment or a shape `model-schema` does not define; the block is listed, never validated.
An `illustrative` mark on a block that contradicts an existing class is a silent pick (`CLAUDE.md` §2).
Every fence in `docs/specs/` declares a language.

**Requirement IDs are append-only.** Never renumber. Never insert `42a`/`42b` — that is not
the convention and the audit will not see them. Find the current maximum and append:

```bash
grep -o 'FR-MODEL-[0-9]*' docs/specs/02-modelling.md | sort -t- -k3 -n | tail -1
```

To retire a requirement, mark it `SUPERSEDED BY <id>` in place. Do not delete it.

**A bolded ID *is* a definition.** The audit treats `**FR-406**` as declaring that
requirement, so bolding an ID when merely *referring* to it elsewhere creates a phantom
second definition and fails the build. Reference IDs in backticks or plain text; reserve
bold for the row that defines them.

A new ID may sit anywhere in the document — position is free, the number is not. Placing
FR-147 next to FR-146 because they are topically related is correct.

**A `pricing-core` interface signature's `def` vs `async def` is a fact to verify, never a
default to assume.** Declare a signature `async def` exactly when it directly awaits an
injected async dependency (a resolver doing real I/O) or a native async binding, from a
caller context that is itself async — plain `def` otherwise. Two `03-rating-engine.md` §5.2
signatures were declared synchronous and both turned out wrong once something checked what
they actually call: `compile_bundle` awaits an `ArtifactResolver` doing genuine async
SQLAlchemy I/O (ruled 2026-08-29, PR #315); `score_one` calls the ZEN engine's
`async_evaluate()`, discovered only by a spike because sync `evaluate()` blocks the event
loop and offloading it to a thread pool is *slower than not offloading it at all* — not
merely unhelpful — because the native call holds the GIL for its full duration (ruled
2026-08-29, `docs/research/zen-evaluate-concurrency.md`). Neither was a wrong default;
both were an unverified one, caught only once an implementation or a spike checked what the
wrapped call actually needed. Before writing a `pricing-core` interface signature that
wraps a native library or a caller-injected dependency, check what that thing needs to be
awaited from — a running instance, a `.pyi` stub, or a small throwaway spike — rather than
defaulting to `def` and waiting for a mismatch to be found later.

**Every spec keeps all ten sections**, in this order (`CLAUDE.md` §3 is the standard; this
is the list it points at):

1. **Purpose & scope** — what the module does and explicitly does not do
2. **Concepts & glossary** — domain terms, matching `00-overview.md` §2 exactly
3. **Functional requirements** — numbered `FR-<module>-<n>` for traceability
4. **Data contracts** — entities, fields, types, invariants; reference or define the
   JSON Schema in `docs/contracts/`
5. **Interfaces** — API endpoints (method, path, request/response shape), pricing-core
   function signatures, frontend views touched
6. **Workflows** — sequence of steps with actors (user / frontend / backend / worker /
   pricing-core); link to the relevant `docs/workflows/` journey
7. **Cross-module dependencies** — what this module consumes from and provides to others
8. **Tech dependencies** — which stack components it uses and for what (feeds
   `skills-map.md`)
9. **Non-functional requirements** — performance, audit, security where relevant
10. **Open questions** — the heading stays; each open question is a decision-needed issue and
    §10 lists its issue number (`#n`) with a one-line summary

If a change adds a tech dependency, §8 of that spec **and** `docs/skills-map.md` must both
change in the same commit, and **every `skills-map.md` row cites at least one spec section
or requirement id** — a row that cites nothing cannot be checked against anything.

**Open questions are GitHub issues (ADR-8449, ND-2).** A choice a spec leaves open is a
decision-needed issue with options, trade-offs and a recommendation; the spec's §10 lists
its number (`#n`). `docs/open-questions.md` and the `OQ-` mirror are frozen: existing §10
rows stay as written, nothing new is added to the register, and no mirror check runs. There
is no gate table to update; the milestone on GitHub carries what is due when.

**Never silently pick a side on an open design choice.** Record options and a
recommendation in the decision-needed issue; do not resolve it in prose.

**Deciding one is a requirement.** The issue is closed with a comment starting `Decided:`
and the date; the pull request that enacts it appends the `FR-` it became and lists the
decision in its Decisions section. **A decision that appends no requirement usually has not
been applied.** A decision that binds more than one module is also a record in `docs/adrs/`
(`adr-write`).

## Specifying a custom objective

Custom objectives are a first-class capability of this platform (`CLAUDE.md` §4, `02-modelling.md` §4.4): a spec may
define user-defined objective and eval functions for XGBoost/LightGBM over the gradient +
hessian interface, and custom loss specifications where the standard families do not fit —
Tweedie variance-power tuning, capped or large-loss-adjusted losses, asymmetric pricing
losses. `02-modelling.md` §4.4 catalogues the permitted forms; `WF-702` is the lifecycle.

**An arbitrary-code objective is a governance risk**, so a spec that introduces one is not
complete until it says four things:

1. **How it is declared** — the restricted expression form or the sandbox, never bare code
   evaluated as given.
2. **How it is validated** — what is checked before a fit is allowed to start.
3. **How it is versioned** — a named, versioned definition reusable across models, with its
   own approval status (`02-modelling.md` §4.4).
4. **How it is audited** — what the audit log records when one is declared, approved and used.

A spec that names a new objective form without those four is the failure mode this rule
exists for: the maths is reviewable and the execution path is not.

## After editing

```bash
python3 scripts/audit-docs.py          # must print "All checks passed."
```

There is no decision-gate table to check any more (ADR-8449).

## Writing style that matches the suite

Say who does what, with what data, and what changes. Numbered requirements, typed fields,
explicit status enums. Avoid "the system should handle…". Small illustrative snippets are
encouraged; full implementations are not.

## Verified

2026-11-07 — the JSON-example marker rule added (`FD-1381`, `PL-2053`): check 40 of
`scripts/audit-docs.py` and `tests/test_spec_examples.py` enforce it. Tree `3c3ee5cb`.

2026-08-29 — the `def`/`async def` verification rule added after the second of two
`03-rating-engine.md` §5.2 signatures was found declared wrong the same way in one day
(`compile_bundle`, PR #315; `score_one`, `docs/rulings/INDEX.md#2026-08-29-w11-prework-rulingsmd`
RL-868). Diagnosed as a missing verification step, not a wrong default: sync-by-default is
still correct for the other nine `pricing-core` interface signatures in the same block, and
none of them is amended.

2026-08-23 — the ten-section enumeration and the `skills-map.md` citation rule moved here
from `CLAUDE.md` §5 and §10, and the custom-objective governance rules from §3, when that
file was cut to its binding rules. No procedure changed; the standard is still §5's, this is
the list it points at.

2026-08-18 — Confirmed while recording five maintainer decisions (OQ-577, OQ-576, OQ-584, OQ-585, OQ-639 →
FR-137/93/196, FR-224, FR-364; 456 → 461 requirements). Both halves of the
"a decision appends a requirement" rule appeared again: FR-364 shipped with its code and its
negative test, while FR-137 and FR-224 are deliberately undelivered and each carries a
phase, an owner and a deadline in the requirement itself. Two of the five ratify behaviour that
was **already built** (FR-93, FR-196) — those still append a requirement, and the
cheap way to keep them honest is a second `@pytest.mark.req` on the test that already proves the
behaviour, so the decision is evidenced rather than merely stated.

2026-08-17 — Confirmed while recording two maintainer decisions (OQ-544 → `01`
FR-64, OQ-563 → FR-78). Both halves of "a decision appends a requirement"
appeared in one commit: FR-78's refusal shipped with it, FR-64's rename is
deliberately not delivered and the requirement says so with a trigger and an owner — which
is what stops a deferred decision from decaying back into a recommendation. The gate-table
count rule above was learnt here.

2026-08-15 — Confirmed while recording six maintainer decisions (OQ-MODEL-1, 2, 4, 5, 6, 7)
as FR-150, FR-151, FR-198, FR-199, FR-135, FR-106, FR-185, FR-91. The gate-table rule above was learnt from the failure, not from
foresight: the invariant was already broken on `main` when this work started.

2026-08-14 — Confirmed again while recording four maintainer decisions: bolding
`**FR-406**` in an open-questions row created a duplicate-definition failure, caught by
the audit. Originally confirmed by applying Track A research findings across four specs: appended
FR-147, FR-148, FR-149, FR-126, FR-273, FR-274, FR-275 and NFR-502 (400 → 408 requirements) with
`scripts/audit-docs.py` passing before and after. The append-only rule was verified the
hard way: an initial attempt used `FR-MODEL-42a/42b/42c`, which the audit's
`(?:FR|NFR)-[A-Z]+-\d+` pattern silently does not match, so the requirements would not have
been registered at all.
