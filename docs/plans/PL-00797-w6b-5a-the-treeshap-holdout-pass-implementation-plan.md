---
id: PL-797
family: plan
kind: leaf
title: W6b-5a — The TreeSHAP Holdout Pass — Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-25
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-25-w6b-5a-treeshap-holdout-pass.md
---

# W6b-5a — The TreeSHAP Holdout Pass — Implementation Plan

**Slice:** `W6b-5a` — FR-168's backend half: `holdout_strength_ratio` on an
interaction candidate.
**Base:** `abea752` on `main` — W6b-4b (#207) merged.
**Owner:** `w6b-executor`, arbitrated by `w6b-lead` 2026-08-25.
**Map row:** [`PL-00786-wk-664-the-revised-slice-map.md`](PL-00786-wk-664-the-revised-slice-map.md):153
(`W6b-5`), dependency `—`, blocker `—`. **Split into `5a`/`5b` on 2026-08-25**, on the map's
own suffix convention and its own criterion — §1.

**Highest ids in use: `FR-168`, `OQ-607`, `OQ-552`, `OQ-655`.**
This plan proposes **`OQ-608`** (F4) and no requirement. Next free after it:
`OQ-612`. `OQ-601` is already **decided (in spec)**; this slice builds what it
decided and does not reopen it.

---

## Global Constraints

- **This is the first cross-stack WK-664 slice.** It changes a `model-schema` shape, so
  **ADR-704's one-way flow applies**: `model-schema` → `docs/contracts/` → the generated
  frontend client. `docs/contracts/` is generated and **never hand-edited**, and FR-451's
  drift guard is live — `generate-contracts.py --check` is part of the gate, not a courtesy.
- **`docs/roadmap.md` is not touched, and neither is `docs/plans/`.** §2 below.
- **The two passes are one code path run twice** (FR-168). A second implementation is
  the defect, not an optimisation — §3.
- The gate runs both halves, every exit code read separately (§11).

---

## 1. The split

`W6b-5` is split at **backend versus panel**, approved on the map's own criterion: a
reviewer can accept one while rejecting the other, and here in its strongest form.

`5a` changes **what a published artifact contains** and moves a contract shape. Its whole
correctness argument is one property — the same code path run twice — because the ratio's
numerator and denominator are otherwise merely adjacent. `5b`'s is a different question for
a different reader: does a ratio near `1` versus near `0` read correctly to an actuary, does
the panel imply a threshold FR-168 forbids, does it respect FR-135's
never-writes-a-Factor. **A reviewer approving a UI panel should not thereby be approving a
change to a published artifact's shape.**

Size supports it independently: `FactorWorkbenchView.vue` is 702 lines and carries **none**
of `5b`'s three features — a grep for intent, interaction and one-way returns two comments.

**FR-168's owner clause resolves to `5b`, not here.** It is description-anchored —
"the slice that builds the factor workbench's suggestion panel" — so splitting discharges
the requirement across two slices while the clause names one. That is recorded **in the
spec**, not in this plan: see §2. Nothing about the discharge depends on this file being
found.

---

## 2. What this slice must amend, and what it must not

When `5a` lands, statements at **six sites** become false. §2 requires them resolved in the
same commit; leaving them is the §0 disagreement the repo exists to prevent. Enumerated from
the rows rather than counted from a summary:

| # | Site | The claim that stops being true |
|---|---|---|
| 1 | **`02`:194** (FR-135's row) | "Until that lands the artifact publishes strength alone" **and** "FR-168 remains unbuilt" — two clauses, one row. |
| 2 | **`02`:232** (FR-168's own row) | "until it lands the artifact publishes `strength` alone and `holdout_strength_ratio` is absent rather than defaulted". **Also carries D3's record** — see below. |
| 3 | **`02`:1396** (§4.9's example note) | "No build produces it yet"; "absent rather than defaulted until … lands"; and "the example as printed is **not** a valid instance of the shape that validates the artifact today". |
| 4 | **`02`:2407-2416** (§5.2's signature note) | "The built signature takes no `holdout`" **and**, at `:2411`, "until that lands the function publishes `strength` alone". The note runs to **:2416**, not :2410 — an earlier draft of this plan stopped short and would have left the second clause standing. |
| 5 | **`02`:3113** (§10's OQ-601 row) | "Until the suggestion panel is built the artifact publishes strength alone." |
| 6 | **`open-questions.md`:94** (OQ-601) | "Owner: the slice that builds the factor workbench's suggestion panel; until it lands the artifact publishes `strength` alone and `holdout_strength_ratio` is absent rather than defaulted." |

**Sites 5 and 6 are not verbatim copies of one another**, which both this plan's first draft
and its review assumed. `:94` carries owner *and* status; `:3113` carries a condensed status
claim and no owner. Both are falsified, both must be amended, and **the amendment text
differs per mirror** — one text applied to both would introduce the divergence the mirroring
rule exists to prevent.

**`02`:2378-2383, the signature block itself, is *not* amended.** It already declares
`*, holdout: pl.DataFrame` with no default — it is **spec ahead of code**, and 5a makes the
code match it. Only its *note* at 4 above, which says the built signature lacks the keyword,
stops being true.

Three further mentions — `:193`, `:2583`, `:3086` — are references without a status claim
and are **not** amended.

**Amended by appending a dated note, never by rewriting**, on the repo's own idiom:
FR-135 carries "*Landed 2026-08-24 (W32-9): …*", and `roadmap.md`:4967-4970 is a §0
resolution of exactly this shape — an "until it lands" clause going stale on merge, resolved
by appending to the same row.

**`docs/roadmap.md` is not touched.** Its five mentions are historical by construction: two
are verdicts inside W32-9's closure record, one line below the record's own statement that
"the record of what was believed on 2026-08-23 is preserved intact rather than rewritten";
the other three are a `git log -L` attribution, a dated note about W6b-11, and an OQ table
row where OQ-601 stays decided. **No WK-664 slice PR has ever touched that file** across
all eight merged slices — a convention, not an accident. Slice-level discharge belongs to
the workstream closure record under §13, and the lead is tracking it there.

**`docs/plans/` is not touched.** The slice map says the same thing at :95-96 and stays
frozen at its date.

---

## 3. Findings

### F1 — the holdout pass cannot reuse `_interaction_candidates` as it stands

`_interaction_candidates` returns **the top five pairs** (`strengths[:5]`). The holdout pass
needs a strength for **the same five pairs the in-sample pass chose**, not the holdout's own
top five — a pair that ranks fourth in-sample and eleventh out of sample is exactly the
collapse FR-168 exists to surface, and taking each partition's top five independently
would silently drop it and compare two different pairs' numbers.

So the reusable unit is **the full pair-strength map**, not the ranked five. The function
splits: one that computes every pair's strength on a given encoded matrix, and a thin caller
that ranks and truncates. The in-sample pass ranks; the holdout pass is a lookup for the
pairs already chosen.

This is what makes "one code path run twice" literally true rather than approximately: the
same sampling, the same `resolve_factors`, the same `_encode` with the same
`categorical_maps`, the same 5 000-row cap, the same off-diagonal sum — differing only in
which frame goes in.

**Same cap is not the same N**, and F4 is why that matters. This finding delivers the
requirement's letter; F4 records that its letter is not sufficient for its purpose.

### F2 — a zero in-sample strength has no ratio

The ratio is "the holdout value over the in-sample one". A pair whose in-sample strength is
`0.0` has no defined ratio, and `ShapInteraction.strength` is `Field(ge=0.0)`, so zero is
representable.

It is reachable only when every candidate is zero — the top five are the largest — which
means a booster that found no interaction structure at all. **Decision 2** covers what is
published then; the wrong answer is a silent `0.0`, which reads as "collapsed out of sample"
when the truth is "there was nothing in sample either".

### F3 — the spec's printed example is currently an invalid instance, and this slice fixes that

`:1396` records it explicitly: `ShapInteraction` sets `extra="forbid"`, the §4.9 example
prints `holdout_strength_ratio`, and therefore "a fixture copied from it would be rejected".
Adding the field closes the gap.

**Pinned by a test that constructs the example as printed**, rather than by a reader
comparing two blocks by eye. That test is the difference between the amendment at `:1396`
being a claim and being a checked fact.

### F4 — the same cap does not mean the same N, and the ratio is measured across unequal samples

**Confirmed in the code, not speculative.** `_interaction_candidates` caps with
`capped = x[: min(x.shape[0], 5_000)]` (`transparency.py`:401), and that is applied **per
call**. Run it on a 50 000-row training partition and it sees 5 000 rows; run it on a 3 000-row
holdout and it sees 3 000.

So an implementation that honours FR-168 exactly — same seed, same cap, same encoding —
still compares a strength measured on 5 000 rows against one measured on 3 000.

**Unequal N makes the ratio noisier, not biased.** An earlier draft of this plan said the
smaller sample gives the bias a direction; that was wrong. `mean(|·|)` is a sample mean and
is unbiased at any N — a smaller holdout widens the ratio's spread and does not shift its
centre.

**The ratio is nonetheless pushed below `1`, and by something equalising N cannot fix.** The
five pairs are selected as the top five **by in-sample strength** (`sort(...)`, then `[:5]`,
`transparency.py`:409-419), and the holdout is a *lookup on those same five*. So the
denominator is a **selected maximum** — the largest of many noisy estimates, and therefore
biased upward by the selection itself — while the numerator is an independent
re-measurement of the same pair, and unbiased. Regression to the mean follows: the expected
ratio is **below `1` even when the structure is identical in both partitions, and even at
equal N**.

That changes which remedies are candidates, which is why it belongs in the open question and
not in a footnote. **Equalising N drops from cure to partial** — it narrows the spread and
leaves the centre where it was. A debiased denominator, or a published null band saying what
ratio to expect under no collapse, are the remedies that address the cause.

It also reaches the requirement's own interpretive sentence: "a ratio near `1` says the
structure survives out of sample; a collapse toward `0` says the pair is a fitting artefact"
is written as though `1` were the unbiased null. Under selection it is not. **That sentence
is not amended by this slice** — it is a maintainer's call, and it is recorded in the open
question rather than acted on.

**Raised as `OQ-608` and built as written** (§10). No remedy is absorbable here: equalising
by lowering the training cap changes `strength` itself, and `strength` is what selects the top
five, so it would silently re-rank candidates in every future artifact; and computing a
separate denominator at holdout-N contradicts "the holdout value over the in-sample one",
where the in-sample one **is** the published `strength`. Both need a spec change, which is
the §10 test.

### F5 — FR-168's rebuild-reuse clause is not true of the SHAP summary today

The requirement says the ratio "on a rebuild … is reused rather than recomputed, with the
rest of the surrogate's stored numbers (FR-138)". But `reusable_numbers()`
(`model_handlers.py`:986) returns the stored **GlmApproximation** block, and
`build_shap_summary` runs at `:1062` **unconditionally** — before and outside that branch. So
the summary is recomputed on every rebuild today, and the ratio would be too.

Two readings, and they differ in scope: the clause may mean the ratio needs no storage or
recompute path *of its own* — it rides with the summary, and is trivially satisfied — or it
may require the summary itself to be reused, which is new work in a slice that is otherwise
a computation change. **Decision 3.**

---

## 4. Decisions for arbitration

### Decision 1 — where the holdout frame comes from

FR-168: "The holdout frame is already loaded beside the training frame wherever the
summary is built … this adds a second pass over a capped sample and no new data path."

**Verified rather than assumed**: `holdout` is assigned at `model_handlers.py`:878 from
`_split_frames` and asserted non-None at `:953`, so it is in scope at the `:1062` call.

**DECIDED: `*, holdout: pl.DataFrame` — required, no default.** This plan first proposed an
optional keyword and was overruled, for two reasons that are both better than the one I had.

**The spec already declares it required.** `02` §5.2:2380 reads `*, holdout: pl.DataFrame`
with no default, and the sibling `build_glm_approximation` takes it required too. An optional
keyword would be a silent §0 divergence from a signature the spec has already published —
this slice exists to make the code match that block, not to renegotiate it.

**And optional makes the failure mode invisible.** A caller that forgets `holdout=` produces
exactly the pre-5a artifact — `strength` alone, no ratio — silently and for ever, which is
**indistinguishable from D2's legitimate absence**. Required makes the same mistake a
`TypeError` at the call site. My standalone-import reasoning does not reach: a keyword
argument adds no dependency, and `pricing-core`'s own tests can pass a frame.

### Decision 2 — what is published when the in-sample strength is zero (F2)

| | Option | |
|---|---|---|
| **(a)** | **`holdout_strength_ratio` absent for that pair** | Honest: there is no ratio. Matches the interim's own shape — absent rather than defaulted — which the spec twice calls the right treatment. |
| **(b)** | `0.0` | Reads as a total out-of-sample collapse. It is the most alarming possible value for the least informative case. |
| **(c)** | `1.0` | Reads as "survives perfectly". Worse than (b): it manufactures reassurance. |

**DECIDED: (a).** The field is already `float | None`, so absence costs nothing and carries
exactly the available information. FR-168's own words for the interim — "absent rather
than defaulted" — are the precedent for preferring absence to an invented number.

**One condition, and it is a real ambiguity the prose does not settle: "absent" must be
pinned to an encoding.** A producer emitting `"holdout_strength_ratio": null` and a fixture
asserting the key is missing entirely *both* satisfy "absent rather than defaulted", and they
are different artifacts on the wire. Whichever is chosen must be **stated and tested**, not
left to whatever `model_dump` happens to do.

**This slice emits the key with `null`.** `ShapInteraction` is a frozen Pydantic model with
`extra="forbid"` and the field is `float | None = None`, so the key is present in a plain
dump and its absence would require `exclude_none` at every serialisation site — a per-site
setting is exactly the kind of thing that holds at one and not another. `null` is one shape
everywhere, and it still honours "not defaulted": `null` is not a number and cannot be read
as one, which is the whole of what the requirement is protecting against. Tested on the
serialised artifact, not on the Python object.

### Decision 3 — whether this slice makes the SHAP summary reusable on rebuild (F5)

**DECIDED: 5a builds no reuse — and the reading is not available silently.**

Making `build_shap_summary` reusable is a change to *when transparency is recomputed*,
affecting every field on the artifact and not only this one. That is FR-138's
territory and belongs in a slice where it is the headline, not absorbed into a computation
change.

But my original framing — read the clause as satisfied and move on — was overruled, rightly.
The clause is **false of the SHAP summary today**, verified twice: `reusable_numbers()`
returns only the `GlmApproximation` block, and `build_shap_summary` runs unconditionally at
`model_handlers.py`:1062, outside that branch. So the summary is recomputed on every rebuild,
the ratio will be too, and **FR-168's own cost argument leans on that clause**.

So the dated append at site 2 **records the clause as unsatisfied, with an owner** — not as
satisfied by a favourable reading, and not silently. A requirement whose cost argument rests
on a behaviour nothing implements is a finding, and it gets written down where the next
reader meets it.

---

## 5. Interactions this slice touches but does not resolve

1. **`5b` builds the panel** and carries FR-168's owner clause. This slice's spec
   amendments say the backend half landed, so `5b`'s reader is not left searching.
2. **LightGBM is unaffected.** It computes no interaction values; `interactions_available`
   already reports that as a capability rather than an empty list, and no candidate exists
   to carry a ratio.
3. **No threshold is introduced anywhere.** FR-168 is explicit that the ratio is
   ranked evidence and never an admission test, and FR-135's refusal to write a Factor
   is untouched by this slice.
4. **The `frontend.yml` trigger recorded unproven in W6b-4b** is exercised here naturally —
   this diff includes `packages/pricing-core/src/pricing_core/modelling/**`. **Not
   manufactured**; noted when it fires, and not claimed in advance.

---

## 6. File Structure

```
packages/
  model-schema/src/model_schema/transparency.py   ShapInteraction.holdout_strength_ratio
  pricing-core/src/pricing_core/modelling/transparency.py
                                                   the split code path, run twice
  pricing-core/tests/test_transparency.py          extended
backend/
  src/app/worker/model_handlers.py                 one argument at the call site
docs/
  contracts/                                       REGENERATED, never hand-edited
  specs/02-modelling.md                            four amendment sites + §10 mirror
  open-questions.md                                OQ-601's mirror
frontend/src/api/generated/                        regenerated, VCS-ignored
```

---

## 7. Tasks

### Task 1 — the shape, and the contract it flows into

`holdout_strength_ratio: float | None = None` on `ShapInteraction`, then
`generate-contracts.py` and `pnpm generate:api`. **`docs/contracts/` is regenerated, never
edited**; `--check` proves the committed contract matches its source (FR-451).

### Task 2 — one code path, run twice (F1, Decision 1)

Split the pair-strength computation from the ranking, add the `holdout` keyword, and compute
the ratio by lookup over the pairs the in-sample pass chose. Zero in-sample strength yields
an absent ratio (Decision 2).

Tests: the ratio is the quotient of two strengths this test computes independently; both
passes use the same seed, cap and encoding — asserted by construction, not by comment; a
holdout identical to the training frame yields a ratio of exactly `1.0`, which is the
sharpest available check that numerator and denominator are comparable.

### Task 3 — the caller, and XGBoost-only

One argument at `model_handlers.py`:1062. A LightGBM summary carries no candidates and so no
ratios; asserted.

### Task 4 — the spec amendments and `OQ-608` (§2, F4)

**All six sites** by dated append, with **different text for sites 5 and 6** since the two
OQ-601 mirrors are not verbatim copies. Site 2 also records D3: FR-168's
rebuild-reuse clause unsatisfied, with an owner. The signature block at `:2378-2383` is not
touched — only its note.

Includes the test from F3 constructing §4.9's printed example, so `:1396`'s amendment is a
checked fact rather than a claim, and the D2 test asserting the serialised encoding of an
absent ratio.

Then **`OQ-608`** in both mirrors: equal caps produce unequal N whenever a partition is
smaller than the cap, so a faithful build compares strengths measured on different row
counts, with the noisier side always the holdout. Carries the evidence — `transparency.py`:401
applying `min(x.shape[0], 5_000)` per call — the three candidate remedies, and the note that
FR-168 names seed, cap and encoding but never equal N. **No remedy is built here.**

`audit-docs.py` runs here.

### Task 5 — the gate, both halves, and the close

All thirteen commands, each exit code read separately. §13 mutations at minimum: the holdout
pass reusing its own top five rather than the in-sample pairs; a different seed on the second
pass; the cap dropped on one side; a zero in-sample strength defaulted to `0.0`. Then PR, CI
read per-workflow — **and this is the first PR whose diff should trigger `frontend.yml` from
a `packages/` path**, which is worth confirming rather than assuming — merge verified by
`state`/`mergeCommit`, cleanup, report.

---

## 8. What would make this plan wrong

1. **If FR-168's rebuild clause requires reuse** (F5), Decision 3 is wrong and the
   slice grows into FR-138's territory.
2. **If the holdout partition can be empty or tiny.** The plan assumes a holdout frame worth
   sampling; a split whose holdout is a handful of rows produces a ratio with no stability,
   and nothing in FR-168 sets a floor. If that is reachable it needs either a minimum
   or an explicit statement that none applies.
3. ~~**If `_interaction_candidates`' 5 000-row cap interacts with the outer sample.**~~
   **Struck — confirmed, not hypothetical, and promoted to F4 and `OQ-608`.** The cap is
   applied per call at `transparency.py`:401, so equal caps give unequal N whenever a
   partition is smaller than the cap. It is no longer a thing that would make the plan wrong;
   it is a thing the plan states, builds around, and files.
4. ~~**If the maintainer reads FR-168's comparability clause as already requiring equal
   N.**~~ **Withdrawn.** The requirement's grammar settles it: "the same seed, the same row
   cap and the same encoding on each partition — **so** the numerator and the denominator are
   comparable" makes comparability the *conclusion drawn from* three enumerated sames, and
   equal N is not among them. F4 shows the inference does not hold, which is a defect in the
   requirement rather than in a build that follows it. And equalising would not deliver the
   property anyway (F4's selection argument), so there is no reading under which it belongs
   in 5a.
