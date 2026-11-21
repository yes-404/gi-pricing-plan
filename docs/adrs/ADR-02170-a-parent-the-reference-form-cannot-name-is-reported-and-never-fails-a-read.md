---
id: ADR-2170
family: decision
title: A governed parent the reference form cannot name is reported in the provenance, and never fails a read
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-21
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 89b215ea
supersedes: [ADR-2160]        # for one point only: #1868's "subject_refs is never empty", for a parent the reference form cannot name
superseded_by: ~
corrected_by: []
relates: [FR-2159, ADR-2160]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2170 — A governed parent the reference form cannot name is reported in the provenance, and never fails a read

- **Status:** Accepted (front matter `active`).
  - It supersedes ADR-2160 for one point only: #1868's rule that `subject_refs` is never empty for a shape with a governed parent. That rule stands for every parent the reference form can name.
  - ADR-2160's text is not edited; its status line and index row say it is superseded in part.
- **Deciders:** on the maintainer's behalf, by delegation, on 2026-11-21 ([#1961, comment 7060609084](https://github.com/yes-404/gi-pricing-plan/pull/1961#issuecomment-7060609084), point 2). It answers the question raised on #1506 on 2026-11-19 ([comment 7016302144](https://github.com/yes-404/gi-pricing-plan/issues/1506#issuecomment-7016302144)).
- **Number:** named in that decision.
- **Related:** `00` FR-2159; ADR-2160 (#1868); #1962, which decides the slug grammar itself.
- **Enacted by:** the pull request of #1506 (#1961): `Provenance.unnamed_subjects` and `compose` in slice 2, the badge's wording in slice 3, and FR-2159's dated note in `00` §3.

## Context

FR-2159 gives the read of each of ten governed shapes a read-side `Provenance` object, composed on every read. #1868 decided that its `subject_refs`, the governed parents in the reference form `{type}:{slug}@{version}`, is never empty for a shape that has a governed parent (ADR-2160).

A model family slug is a bare string: nothing holds it to the reference form's slug grammar. A model can therefore be stored under a slug that no reference can name.

- A run on #1961's branch showed the consequence: a model reserved as `Motor_Freq` was stored, and after its fit its diagnostics read answered 500. `main` answered the same read 200, because it carried no provenance.
- The transparency artifact, backtest and model comparison reads name a model the same way.
- A stored reference string that cannot be parsed for another reason, such as a version that is not an integer, fails the same way.

So, read literally, #1868's rule would turn a read that works today into a failure.

Options considered:

- **Report the parent, accepted.** The read answers 200, and the parent the reference form cannot name is reported in `unnamed_subjects`.
- **Hold family slugs to the grammar when a model is created.** It is outside #1506's paths and a contract change, and rows already stored would still fail. #1962 decides it separately, as the rule for new models, and rows already stored keep their slugs.
- **Fail the read.** Not taken: a read that worked before provenance existed would stop working.

## Decision

- **A read never fails because a stored governed parent cannot be written as a reference.** It answers 200, and the parent is left out of `subject_refs` and counted in `Provenance.unnamed_subjects`. That field is optional, at least 1 when present, and null when every parent is named.
- **The view says it in words,** "N governed parent(s) could not be written as a reference", beside the references it can name. It is never left blank.
- **#1868's "`subject_refs` is never empty" stands** for every parent the reference form can name. Only a parent it cannot name is reported instead of listed.

## Consequences

- **Positive:** every read that answered before provenance existed still answers, and a parent that cannot be named is visible rather than silently dropped.
- **Negative:** a reader cannot tell from the count alone which parent could not be named, or, in an ordered shape such as a model comparison, at which position. The count also covers a stored reference that is corrupt for any reason, not only an off-grammar slug, so a corrupted reference is reported rather than raised as an error.
- **Neutral:** once #1962 holds family slugs to the grammar at creation, only rows stored before then can produce a count.
