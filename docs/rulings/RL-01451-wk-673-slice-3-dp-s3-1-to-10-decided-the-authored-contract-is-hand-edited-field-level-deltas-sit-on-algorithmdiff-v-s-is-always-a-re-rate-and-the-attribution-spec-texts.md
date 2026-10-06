---
id: RL-1451
family: ruling
title: WK-673 Slice 3, DP-S3-1 to DP-S3-10 decided — the authored contract is hand-edited, field-level deltas sit on AlgorithmDiff, v(S) is always a re-rate, and the attribution spec texts
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-06            # original date 2026-10-05, set at the draft; minted 2026-10-06
owner: decision-maker
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [SL-1387, PL-1267, RL-1394, RL-1264, RL-1402, RL-1263, RS-1201, FR-219, FR-266, FR-1397, FR-1398, FR-1399]
---

# RL-1451 — WK-673 Slice 3: DP-S3-1 to DP-S3-10 decided, and the attribution spec texts

*(Minted 2026-10-06 as RL-1451 from working id 9663, in the B1 batch mint PR; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

**Decided by the maintainer, by delegation**, in four entries of
`~/gi-pricing-plan.local/channel/to-lead.md`, each cited below by its header and item. **This
record decides nothing.** It files those decisions as one ruling, as PL-1452's activation need
3 asks, and adopts the plan's proposed texts P1–P6 as the texts Slice 3 applies.

## How this was ruled

**Written 2026-10-05, at effort `medium`**, by the decision-maker session `dm-s3`, on the
lead's brief of 2026-10-05, which the maintainer (by delegation) approved in item 29 of the entry headed
*"2026-10-05 13:25:23 BST — 29: RL-1451 OK; 30: extend option (b) to S3 vs S2, with one
serialisation; 31: close #986 OK"*: *"dm-s3 (opus) on RL-1451, recording DP-S3-1..10 as
decided (citing my entries by header) and adopting P1–P6 verbatim: OK. The spec texts are
T-texts for S3's code commit, as for RL-1449."* **Working id 9663 is the lead's allocation.**

Every fact was read at `origin/main` `caa4e411a9c07a389cf47092a923c7761b2b92dc`
(`git rev-parse origin/main` after `git fetch`, 2026-10-05 13:26:44 BST). The plan was read at
PL-1452's draft PR #1138, branch `pl-9689-wk673-s3-leaf`, head
`f3603e7cd99373a79a563b432ac234bc805a962d`; its decision-point table is §"Decision points"
and its texts are §"Appendix — proposed texts P1–P6". *Re-read 2026-10-05 15:08 BST at the
plan's head `e810b7851f71c995b284da7121d2e6d51a145318`: P2, P4 and P6 are unchanged; P1, P3 and
P5 were revised toward this record's texts. The comparisons below stay against `f3603e7c`, and
this record's texts govern (§"What it obliges").* RL-1449 was read at draft PR #1126,
branch `dm-9715-oq9739-subset-input-contract`, head
`2ab3818a63387d3ce57e806b6e7679475b45b4dd`. Unminted records (PL-1452, RL-1449, RL-1418) are
cited in working-id form and kept out of `relates:` (check 32).

**RL-1449 applies to Slice 3 as well.** Its T1–T3 (FR-1399's DP-2 clause and delta
derivation, FR-1398's subset contract) are Slice 3's to apply, and its five acceptance
violations are Slice 3's tests. This record does not restate them; it orders its own texts
after them where they share a row.

## Ruled

| DP | Ruling | Decided in |
|---|---|---|
| DP-S3-1 | **(a)** S3 hand-edits the authored `dislocation-run.schema.json`: the `kind` enum gains `input_field` and `output`, and attribution's `mean_change_pct` and `cumulative_change_pct` become number-or-null | 13:12:56 item 16; 13:24:03 item 3 |
| DP-S3-2 | **(a)** two list fields on `AlgorithmDiff`, computed by `diff_algorithms`; the FR-219 route's 200 is typed as `AlgorithmDiff` | 13:15:53 item 17 |
| DP-S3-3 | **(b)** re-rates only; replay is measured, not built | 13:15:53 item 18 |
| DP-S3-4 | **(a)** `ATTRIBUTION_RECONCILIATION_FAILED` | 13:15:53 item 19 |
| DP-S3-5 | **(a)** n = 2; S and R exact, rounded once to 6 places, half-even; null when D = 0 | 13:15:53 item 19 |
| DP-S3-6 | **(a)** a measurement-only ZEN freMTPL2 algorithm with `model_call`, a declarative JSON fixture | 13:15:53 item 19 |
| DP-S3-7 | **(a)** fail the run with the attribution code, naming the `quote_id` and the subset | 13:20:26 item 23 |
| DP-S3-8 | **(a)** an in-memory subset `RatingVersion` with an overlay resolver | 13:20:26 item 23 |
| DP-S3-9 | **(a)** a `model_reference_mode` difference is refused up front | 13:20:26 item 23 |
| DP-S3-10 | **(b)** re-rates on the first 20,000 policies for K = 3..6, one full-portfolio K = 3 run; every full-K figure is derived and labelled | 13:20:26 item 24 |

The options are PL-1452's, at the head named above. Each section below quotes the maintainer's (by delegation)
words verbatim.

### DP-S3-1 — the contract path: (a)

Header *"2026-10-05 13:12:56 BST — DECISIONS 15 and 16; CORRECTION to my 13:03:23 item 11; a
priority rule for HIGH G2 blockers"*, item 16:

> 16. DP-S3-1 (PL 9689): OPTION (a). S3 hand-edits the authored file in its own code commit, as S1 and S2 did; test_contracts.py:98's marker stays; S4 generates and compares it under PL-1267. The S3 ledger names the hand edit.

The same entry corrects the reason RL-1449 T4 gave: *"That reason is FALSE for this file at
caa4e411: backend/tests/test_contracts.py:98 reads "dislocation-run": "03 §4.6 — hand-authored
until WK-673 Slice 4 generates and compares it (PL-1267)", and SL-1385 (#1094) and SL-1386
both edited it."*

The addendum, header *"2026-10-05 13:24:03 BST — RL 9668 (#1137) noted for its ACK; DP-S3-1
addendum ACCEPTED; CR-838:46 is a data point for FD-1282"*, item 3:

> 3. DP-S3-1 addendum: ACCEPTED. Attribution `mean_change_pct` and `cumulative_change_pct` become number-or-null in the same hand edit, red first. Verified: §4.6 (03 :570) rounds every ratio once to 2 dp and makes a zero-denominator ratio null; the schema's band and factor `mean_change_pct` are already `{"type": ["number", "null"]}` (dislocation-run.schema.json :49, :63; S2, RL-1402 S5). The Decimal-string rule for percentages is RateTableDiff's (model-schema rating.py:735 docstring), a different artifact.

### DP-S3-2 — where the field-level deltas live: (a), with a condition

Header *"2026-10-05 13:15:53 BST — DECISIONS 17–21 (PL-1452 DP-S3-2/3/6; FD-1420 DP-1; RL-1428
follow-ups)"*, item 17:

> 17. DP-S3-2: OPTION (a), two list fields on AlgorithmDiff computed by diff_algorithms (FR-1399 derives "from the structural diff"). Condition: the FR-219 route's 200 is a CHANGED JSON route, so under WK-1178's template line ("every new or changed JSON route has typed request and 2xx response schemas") S3 types that 200 as the model-schema AlgorithmDiff in the same commit, with contracts regenerated; existing keys and values unchanged (a test pins them).

### DP-S3-3 — ladder replay: (b), with conditions

Same header, item 18:

> 18. DP-S3-3: OPTION (b), re-rates only. Verified: RL-1394 T1 (:342) says v(S) "may come from a proven ladder replay", so re-rating is the default and replay is optional; dislocation-run.schema.json already enumerates subset_valuation "rerate" | "ladder_replay". Conditions: the evaluation harness MEASURES replay on the six F3 sets (per set: aligned or not, replay v(S) vs re-rate v(S) agreement in minor units, wall time), and the numbers go in the ledger and the dated §4.6 note. Every run records subset_valuation "rerate". The ≈2 worker-hours for K=4 is an estimate: the ledger carries the measured figure.

### DP-S3-4 and DP-S3-5 — the code and the order count: (a) and (a)

Same header, item 19, its last sentence:

> The non-blocking choices (ATTRIBUTION_RECONCILIATION_FAILED, n=2) are accepted as in the plan.

### DP-S3-6 — the measurement algorithm: (a), with conditions

Same header, item 19:

> 19. DP-S3-6: OPTION (a), a measurement-only ZEN freMTPL2 algorithm mirroring the spike, with model_call. Conditions: it is a declarative JSON artifact (CLAUDE.md §2: never a pickle, never code), kept as a test or benchmark fixture under a name the exit-demo slice can adopt or promote, so it is built once; S3 does not touch seed.py; the ledger says where it lives.

### DP-S3-7, DP-S3-8 and DP-S3-9 — a policy not quoted, the subset version, a version-level difference: (a), (a), (a)

Header *"2026-10-05 13:20:26 BST — DECISIONS 22–27; severity signals for the four gap
findings"*, item 23:

> 23. DP-S3-7: OPTION (a). Fail the run with the attribution code, naming the quote_id and the subset; a partial attribution would mislead. The dated FR-1397/98 sentence is a T-text a DM adopts (not a spec edit in the plan PR). DP-S3-8 (an in-memory subset RatingVersion with an overlay resolver) and DP-S3-9 (a model_reference_mode difference refused up front): accepted as non-blocking, as proposed.

### DP-S3-10 — the measurement's size: (b), with conditions

Same header, item 24:

> 24. DP-S3-10: OPTION (b). Conditions: PL-1267 is frozen, so Acc 5's change is a dispatch-record delta against PL-1267 citing this entry; every full-K figure is labelled DERIVED with its formula and the measured inputs; no NFR pass or fail is claimed from a derived figure (G4 host fallback applies: measured, diagnostic, carried); the ≈80 h and ≈2 h are estimates and the ledger carries measured times.

### The owned-codes tail serialises

Header *"2026-10-05 13:25:23 BST — 29: RL-1451 OK; 30: extend option (b) to S3 vs S2, with one
serialisation; 31: close #986 OK"*, item 30, the part that binds P1:

> ONE SERIALISATION: the owned-codes list (03 :928 onward) is a single list whose TAIL any code-registering slice appends to. S3 appends there, and the FD 9708 fix registers MODEL_REFERENCE_MODE_INCONSISTENT (decision 25), so those two appends edit the same tail and SERIALISE: the second merges main and re-appends. State it in both dispatch records.

## The spec texts

**None of these lands in this PR.** They are T-texts for Slice 3's code commit (item 29), as
RL-1449's are: each lands in one commit with the code it describes (`CLAUDE.md` §2), with
`<date>` that commit's date. Each find string below has exactly one hit in
`docs/specs/03-rating-engine.md` at `caa4e411` (`grep -cF -- '<find string>'` prints `1`), and again at
this branch's base `99afcde215c0817c5ac4db55332ab7a69e4752a0` (#1066, which does not touch `03`),
re-run 2026-10-05 after 13:29 BST, and again at `origin/main`
`809a3794af6d3a6ba688663b0d9b59f951190680` at 15:08 BST, each at the line given (`03` changed
between them only at `:136`, FR-239's finding id re-pointed, #1150).
Where an earlier slice or RL-1449 appends at the same place first, the text goes after that
append, and the dispatch record re-reads the anchor at its tree.

P2, P4 and P6 are adopted **verbatim** from PL-1452. **P1, P3 and P5 are amended**, each for
the reason under it. The amendments were raised by this session as a sub-DP to the lead and
answered by the lead in a team message received before 2026-10-05 13:29:02 BST
(`TZ=Europe/London date`, read on receipt): *"yes to both. Neither is a new decision; each implements one already made."*
P5's text is planner-1387's, sent by the lead in that answer, adopted with one substitution
(below).

### P1 — `03` §5.1, the owned-codes list: appended after the list's last entry (DP-S3-4 (a), DP-S3-7 (a)) — AMENDED

Find **`Error codes owned by this module:`**; the list runs from there to its last entry. At
`caa4e411` the last entry ends with find
**`` `app.platform.rating_versions.require_compilable` is the only raiser)*. ``** (`:965`). `RL-1361`
T11, as RL-1418 re-anchors it (its DP-C) for Slice 7, appends first, and the FD-1421 fix's
`MODEL_REFERENCE_MODE_INCONSISTENT` serialises with this append (item 30): P1 goes after
whatever is the last entry at the dispatch tree.

**Amended**, and why: PL-1452's P1 says the code means only that the parts do not sum. Item 23
makes the same code fail a run whose compared policy is not quoted under some subset (P5), and
item 19 accepted one code, not two. Verbatim, P1 would register a meaning P5 contradicts. The
amendment widens the meaning to both raisers, in planner-1387's words as the lead relayed them
(*"…does not reconcile, or a compared policy has no premium under some subset bundle
(FR-1398)…"*), and nothing else.

```markdown
`ATTRIBUTION_RECONCILIATION_FAILED`
*(added <date>, WK-673 Slice 3, FR-1397, FR-1398, `RL-1394` DP-S1-6, RL-1451 — a Dislocation Run's attribution does not reconcile: for some compared policy the Shapley parts do not sum to its candidate minus baseline payable premium, or its isolated figures plus the residual line do not, as integers; or a compared policy has no premium under some subset bundle (FR-1398). The run fails naming the first such `quote_id`, and in the second case the ids of the changes in that subset, and persists nothing. Raised by `pricing_core.rating.analysis.attribute`; the platform maps it with Slice 4's route)*
```

### P2 — `03` §4.6, a dated note after the paragraph that opens the section (DP-S3-5 (a)) — verbatim

Find **``*(Amended 2026-10-03, WK-673 Slice 1, `RL-1394`: reconciled with `dislocation-run.schema.json` ``**
(`:516`, the paragraph directly under `### 4.6 \`DislocationRun\``); insert after that
paragraph, as its own paragraph.

```markdown
*(Amended <date>, WK-673 Slice 3, `RL-1394` DP-S1-5: the order count.)* Under `order_dependent`, S's lower bound is taken over exactly 2 orders, the declared order and its reverse, so `orders_sampled` is 2. S and R are exact ratios of integers rounded once to 6 decimal places, half-even; where D is 0 each is null.
```

### P3 — `03` §4.6, the same note continued (DP-S3-3 (b)) — AMENDED

Directly after P2's text, in the same paragraph.

**Amended**, and why: item 18 puts the measured numbers *"in the ledger and the dated §4.6
note"*. PL-1452's P3 puts them in the ledger only. The amendment adds the figures item 18
names. **The figures are measured at the slice, not here**: each `<…>` below is a named
placeholder that Slice 3 fills from the measured numbers in its ledger, in the same commit, and
never with an estimate. The six rows are the six F3 change sets in the ledger's order.

```markdown
Ladder replay is not adopted: every v(S) is a re-rate of its subset bundle, so `subset_valuation` is `rerate` and `replay_fell_back` is `false` on every run. Slice 3 evaluated replay against re-rates on the six F3 change sets and recorded the result in its ledger, <LEDGER_ID>. Measured on <MEASURED_TREE>, per set: <SET_1 … SET_6: the set's name; step-aligned yes or no; where aligned, the largest absolute difference between replay v(S) and re-rate v(S) over every subset and policy, in minor units; the wall time of the replay and of the re-rates, in seconds>.
```

### P4 — `03` §5.2: the `analysis.py` block and a paragraph (RL-1264 item 3) — verbatim

The signature goes in the `# pricing_core/rating/analysis.py` block directly after
`attribute`'s three lines; find
**`async def attribute(baseline: RatingVersion, candidate: RatingVersion,`** (`:1060`) and
insert after the third line of that signature (`:1062`).

```python
def estimate_attribution_ratings(k: int, policies: int, *,       # added <date> (WK-673 S3,
                                 grouped: bool) -> int            # RL-1264 item 3)
```

The paragraph goes after the paragraph found by
**``*`analysis.py`'s public surface (added 2026-10-04, WK-673 Slice 2, `RL-1402`).*``**
(`:1124`), as its own paragraph.

```markdown
*`attribute` (added <date>, WK-673 Slice 3).* It reads the portfolio with `read_portfolio`, derives the changes (FR-1399), checks the groups and their dependence before compiling anything, and rates each subset bundle with `score_batch` over the compared set's policies, each pass given only its subset's declared inputs. `AttributionError` is a `ValueError` with `code`: `VALIDATION_FAILED` (partition, dependence, a version-level difference), `BUNDLE_COMPILE_FAILED` (a subset, named by its change ids) or `ATTRIBUTION_RECONCILIATION_FAILED`. `estimate_attribution_ratings` returns the rating count the run will perform, 2^K × policies, or under the above-six rule (3K − 2) × policies, so a caller can show it before launch.
```

### P5 — `03` FR-1398, appended at the row's end, after RL-1449's T3 (DP-S3-7 (a)) — AMENDED

Find **`| **FR-1398** |`** (`:191`); insert before the row's final ` |`, after RL-1449's T3.

**Amended**, and why: the text is planner-1387's DP-S3-7 T-text, which the lead sent in the
answer above, replacing PL-1452's P5. It says the same thing more exactly: it defines the
compared set by §4.6's own term (*"The **compared set** is the quoted-both policies"*,
`03` `:568`), fixes which policy is named (the first in `quote_id` order), and says v(S) is
never assumed, which item 23's *"a partial attribution would mislead"* requires. Adopted with
one substitution: `<RL id>` is this record, written `RL-1451` until the mint, as
RL-1449's T-texts write theirs.

```markdown
*(Amended <date>, WK-673 Slice 3, RL-1451, DP-S3-7 (a).)* **A compared policy is attributed only from its own premium under every subset.** Where a policy quoted in both the baseline and the candidate pass (the compared set, §4.6) is not quoted under some other subset bundle, so that its v(S) is undefined, the run fails with `ATTRIBUTION_RECONCILIATION_FAILED`, naming the first such `quote_id` in `quote_id` order and the ids of the changes in that subset; the policy is never dropped from the attribution and its v(S) is never assumed.
```

### P6 — `03` FR-1399, appended at the row's end, after RL-1449's T1 and T2 (DP-S3-9 (a)) — verbatim

Find **`| **FR-1399** |`** (`:192`); insert before the row's final ` |`, after RL-1449's T2.

```markdown
*(Amended <date>, WK-673 Slice 3.)* A difference between baseline and candidate that no derived change can carry, `model_reference_mode`, refuses the run with `VALIDATION_FAILED`, naming the field, before any subset is computed.
```

## Acceptance — the violation that must become detectable

This record builds nothing. Slice 3 carries these, each shown red on deliberately broken
input, beside RL-1449's five:

- *Violation: the authored contract refuses a derived kind or a null ratio* (DP-S3-1). A run
  carrying an `input_field` change and a zero-denominator attribution ratio validates against
  `dislocation-run.schema.json`; red before the hand edit.
- *Violation: the FR-219 diff route's 200 changes an existing key, or is untyped* (DP-S3-2).
  A test pins the existing keys and values; the route's 200 is `AlgorithmDiff` in the
  regenerated contract.
- *Violation: a run records `ladder_replay`* (DP-S3-3). Every run records `subset_valuation`
  `rerate`.
- *Violation: an unreconciled policy, or a compared policy not quoted in a subset, yields a
  run* (DP-S3-4, DP-S3-7). `attribute` raises `ATTRIBUTION_RECONCILIATION_FAILED` naming the
  `quote_id` (and, for the second, the first such in `quote_id` order and the ids of the
  changes in that subset), on a policy whose parts are broken to sum to `total ± 1`, and on
  one made unquoted in one subset.
- *Violation: a `model_reference_mode` difference reaches compile* (DP-S3-9). `derive_changes`
  refuses with `VALIDATION_FAILED` naming the field, before any subset.

## What it obliges

- **The lead, at the mint:** mint this record, replacing its working id everywhere this
  commit writes it, including inside P1 and P5; mint it before PL-1452, which cites it (13:15:19 BST, *"A record that cites
  another mints after it, always"*).
- **PL-1452's planner:** cite this record as activation need 3's ruling; the executor applies
  this record's texts, never the plan's Appendix.
- **Slice 3 (SL-1387):** apply P1–P6 as given here, after RL-1449's T1–T3, in the commit that
  builds them; hand-edit the authored contract and name the hand edit in its ledger
  (DP-S3-1); type the FR-219 route's 200 and regenerate the contracts (DP-S3-2); measure replay
  and fill P3's named placeholders from its ledger's measured figures (DP-S3-3); keep the freMTPL2 algorithm as a
  declarative JSON fixture, say in its ledger where it lives, and leave `seed.py` untouched
  (DP-S3-6); label every full-portfolio figure DERIVED with its formula and measured inputs,
  and claim no NFR pass or fail from one (DP-S3-10).
- **The dispatch record for Slice 3:** carry `PL-1267` Acceptance 5's change as a delta
  citing item 24 of the 13:20:26 BST entry (DP-S3-10), and state the owned-codes
  serialisation with the FD-1421 fix (item 30 of the 13:25:23 BST entry).

## Spec changes in this commit

None. P1–P6 are Slice 3's to apply.
