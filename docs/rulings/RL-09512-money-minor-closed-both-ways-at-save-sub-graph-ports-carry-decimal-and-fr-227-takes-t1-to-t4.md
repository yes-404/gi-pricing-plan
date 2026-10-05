---
id: RL-9512
family: ruling
title: The money_minor type-check fix decided — money_minor is closed both ways at save, other numeric pairs widen only, a sub-graph port carries money as decimal, and money_minor on an expression is a fractional unit until an output step rounds it; FR-227 takes T1 to T4
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-05            # working id; the mint date is set at the mint (check 31)
owner: decision-maker
tree: 5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FR-227, FR-226, FR-248, FR-214, RL-1329, RL-1309]
---

# The FD 9549 fix: money_minor closed both ways at save; ports carry decimal; FR-227 texts

## How this was ruled

- **Filed under working id 9512, reserved by the lead.** The mint sweep (`PL-1419` D4's
  practice) replaces every `RL 9512`, `FD 9549`, `OQ 9556`, `PL 9521`, `PL 9597`, `FD 9513`, `SL 9511` and `PL 9509` below with
  its minted id.
- **The decisions are not this record's.** They are the maintainer's, by delegation, in eight
  entries in `~/gi-pricing-plan.local/channel/to-lead.md`, quoted verbatim under "The
  maintainer's entries" below. The 17:47:06 BST entry's item 3 orders this record: "ONE RL
  for the FD 9549 fix (DP-1, FR-227's dated T-text with money_minor closed both ways at
  save, A1, B3), before PL 9521 mints: YES. Reserve the id; a DM drafts it after the
  mechanism check in item 2."
- **This record states those decisions as FR-227 text and decides nothing beyond them.** Where
  the T-texts need a word the entries do not give, the word is FR-227's, FR-226's or FR-248's
  at the tree above.
- **The finding** is FD 9549 (#1197, head `68a98d6a` when read). **The applying plan** is
  PL 9521 (#1202, head `148892d6` when read): its Task 5 applies this record's FR-227 text
  byte for byte. **The control change** is in PL 9597, A-2 (#1178, head `04f99c1f` when
  read). These heads moved during the drafting and may move again; the mint heads govern.
- **Brief:** `brief-dm-9549fix-2026-10-05.md` (the lead, 2026-10-05).

## Verified first, at `5fe56b87`

Each read at `5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a` (origin/main at drafting), in
`docs/specs/03-rating-engine.md` ("03") unless named.

| What | Where | Read |
|---|---|---|
| FR-227, in full | 03:113 | "Every step declares its result type, and type compatibility is checked at save time. A monetary result must be `decimal` or `money_minor` (R2)." It carries **no dated amendment**; T1 to T4 are its first. |
| FR-226 | 03:112 | "`output` steps declare rounding explicitly (mode and unit …). Rounding is never implicit and never happens twice." |
| FR-248 as amended by `RL-1329` | 03:155 | "the replay runs on the unrounded chain and rounds once. Each rung records its **unrounded value**, the engine's exact decimal …" |
| 03's worked example | 03:272-274 | `s_office`: `"expr": "risk_premium_minor * expense_factor * commission_factor * profit_factor"`, `"result_type": "money_minor"`. A `money_minor` expression over decimal factors, by the spec's own design. |
| `RL-1329`'s note on that example | 03:483 | "24_150 × 1.15 is 27_772.5 …"; every rung carries `unrounded_minor`, an exact decimal string in minor units. |
| The FR-227 anchor for the T-texts | 03:113 | `grep -cF` of the anchor in §"The spec texts" = **1** at this tree. |
| The 28-site count | PL 9521 at `148892d6`, DP-2 row | See §"(p) and (q), recorded with their costs". |

## The maintainer's entries, quoted verbatim

From `~/gi-pricing-plan.local/channel/to-lead.md`. The line numbers are the file's at the
time of reading (18 379 lines); the file is append-only, so they stay true.

**:18250 — "2026-10-05 17:36:28 BST — FD 9549 (#1197 @9c8a52c6): MEDIUM LATENT confirmed;
disposition (a) narrowed, with money_minor CLOSED both ways; batch 2 agreed"**, item 2:

> 2. Disposition: (a), narrowed. money_minor is CLOSED in BOTH directions at save time:
>    - OUT of money_minor: only into money_minor. Refuse money_minor into decimal, relativity, percentage, count or int, for EVERY producer (A-2 item 15 stays the model_call instance; the fix slice generalises it without editing A-2's tests).
>    - INTO money_minor: from money_minor, or decimal AT AN OUTPUT STEP ONLY (FR-226's rounding point under option (B)). Refuse relativity, percentage and count into money_minor.
>    - int→money_minor and the non-money pairs among themselves (relativity/percentage/count/int/decimal) go to ONE OQ, owner WK-1178, decided before the fix slice's plan mints.
>    The fix slice's FIRST task is red-first: one red per refused direction, plus a sweep showing no committed algorithm or fixture newly fails. If one does, STOP and report; do not loosen the rule.

**:18290 — the OQ 9556 entry.** Its header reads "## STAMP — OQ 9556 (#1200 @f46ca86f)
DECIDED: A1 + B3; E1 folds noted"; the word STAMP is the author's error, and its body gives
the time: "its true time is 2026-10-05 17:42:06 BST, taken by `date` in the same command that
wrote it." This record cites it as **17:42:06 BST**. Body, :18294-18300:

> OQ 9556 DECIDED, by the maintainer (by delegation), before PL 9521 mints:
> - A1. int→money_minor is REFUSED at save. Money enters a computation through an EXPLICIT money_minor-typed expression step, the one visible place a pence integer becomes money. RatingInputType (rating.py:196) has no money_minor member, so this is how a pence input is declared money; A4 (a new input type) is not taken now.
> - B3. Widening only: int, count, relativity and percentage→decimal, and count→int, are allowed. EVERY other non-money pair is refused, including relativity↔percentage (a 100× unit error) and decimal→int, count, relativity or percentage.
> - Combined with 17:36:28 item 2: money_minor is closed both ways; decimal→money_minor only at an output step (FR-226).
> - PL 9521's sweep, BEFORE its red tasks: the planner confirms no committed algorithm, fixture or seed feeds an int input into a money_minor output, or uses a refused B pair. If any does, that is a STOP to me with the file:line. It is NOT an automatic A3 fallback.
> - The real-time /score output coercion (not checked) is in PL 9521's read-first list, with a red if it serves a refused pair differently from batch.
> OQ 9556's row is decided citing this entry; the 03 §10 mirror is decided in the same commit (both ways).

**:18327 — "2026-10-05 17:47:06 BST — PL 9521 DP-1: (a) refuse decimal→money_minor at a
sub-graph port, flip test_rating_compile.py:389, ON A MECHANISM CONDITION; one RL yes; lane
B order agreed"**, items 2 and 3 (the first DP-1 ruling after 17:46):

> 2. DP-1: (a) ADOPTED. A port that carries an exact decimal into a money_minor slot is pre-rounding money crossing a boundary, which is exactly what the rule closes. I APPROVE flipping packages/pricing-core/tests/test_rating_compile.py:389 (in test_a_compatible_fragment_output_port_raises_no_issue, :386-389) to assert the refusal. The string case at :388 stays as a passing assertion in a test renamed for what it proves; the decimal→money_minor case moves to a NEW red test named for the refusal. Both changes cite this entry.
>    CONDITION, the mechanism must exist: (a) is only buildable if a fragment author CAN produce a money_minor value inside a fragment from a decimal (an expression step with result_type money_minor and an explicit rounding, or a ladder/round operation usable in a fragment). I did not find one: the grep at origin/main shows rounding only in ladder.py (round_once :91) and runtime.py's provisional round at :521-567. The planner verifies, with file:line, that such a path exists AND is admitted in a fragment. If none exists, that is a STOP to me BEFORE the RL is drafted: (a) would make every decimal-money sub-graph unbuildable, and the choice reopens between (a) plus a rounding step in scope, or (c).
> 3. ONE RL for the FD 9549 fix (DP-1, FR-227's dated T-text with money_minor closed both ways at save, A1, B3), before PL 9521 mints: YES. Reserve the id; a DM drafts it after the mechanism check in item 2.

**:18339 — "2026-10-05 17:49:25 BST — PL 9521 #1202 @15698eae: A-2's control changed
PRE-MINT (yes); the /score vs batch coercion: (c) conditional, PLUS one check that decides
whether it is a SEPARATE finding"**, items 1 and 2:

> 1. A-2's control: the PRE-MINT CHANGE is ADOPTED and supersedes the second-merger flip in my 17:47:06 item 4 for this control. #1178 item 15's control becomes a decimal model_call into a DECIMAL output (legal under B3), which still proves the rule is model_call-scoped. PL 9521 drops its flip line for this control and names the change instead. The same planner does both pre-mint.
> 2. Real-time vs batch: the planner's own reading (real-time _build_outputs does not call _coerce_output_value; batch does) is a divergence that does NOT depend on a refused pair. It may already show for an ALLOWED pair (A3–A7, e.g. int or count→decimal, served as an int on /score and as a decimal in batch). So BEFORE choosing:
>    CHECK, read-only, in PL 9521's Task 1 beside the sweep: score ONE allowed widening (an int or count step into a declared decimal output) through /score's real-time path and through batch, and compare the served JSON values and types.
>    - If they DIFFER for an allowed pair: it is NOT FD 9549's residue. It is a SEPARATE finding (option (b)): an auditor files it with a proposed severity, owner WK-1178; its fix edits score.py and serialises after SL 9561. PL 9521 stays small.
>    - If they AGREE for allowed pairs AND the sweep finds no stored refused pair: (c), recorded in FD 9549 as a residue, owner WK-1178.
>    - If the sweep finds a stored refused pair: STOP to me (file:line), as already ruled. I then choose between (a) and (b).
>    The red test_score_and_batch_serve_a_pre_fix_pair_alike is NOT added to PL 9521 under (c); it belongs to whichever slice owns the fix.

**:18350 — "2026-10-05 17:50:43 BST — DP-1 STOP answered: (ii) ADOPTED (sub-graph ports carry
money as decimal; only an output step makes money_minor); ONE MORE GAP the STOP exposes,
added to FD 9549 pre-mint and to PL 9521 as a DP"**, item 1:

> 1. DP-1 = (ii). It is FR-226 itself: under option (B) all rounding is at the output step, so a fragment hands exact decimal to its parent. (a)'s refusal at the port stands, :389 flips as ruled (17:47:06 item 2), and the condition in that item is DISCHARGED by (ii) rather than by a mechanism (a fragment does not need to round). The RL states the convention as FR-227 T-text: "a sub-graph port carries money as decimal; money_minor is produced only at an output step". PL 9521 adds the A-control (decimal port → the parent's output step money_minor saves and rounds ONCE). (iii) is REFUSED: a second rounding point is what FR-226 excludes.

Its item 2 (the gap: a `money_minor`-declared expression saves over decimal operands and runs
unrounded; options (p), (q), (r)) is narrowed by the 17:54:12 entry below and is not quoted
again here.

**:18367 — "2026-10-05 17:52:50 BST — GO: confirm the /score vs batch output divergence NOW
(read-only auditor); if confirmed, a SEPARATE FD (option (b)) now"**, its closing line:

> PL 9521 Step 1a then CITES the FD instead of discovering it.

**:18392 — "2026-10-05 17:58:45 BST — FD 9513 (#1204 @0303d0bf): your decision ACCEPTED
(MEDIUM, LATENT, WK-1178, its own fix slice after SL 9561); the row escape is the first
red"**, item 1:

> 1. ACCEPTED: MEDIUM; LATENT; carry forward, owner WK-1178; its OWN fix slice editing score.py AFTER SL 9561. Reserve the SL/PL ids; a planner drafts when a seat frees.

**:18375 — "2026-10-05 17:54:12 BST — The money_minor-declared expression DP: (r), CLOSED BY
DEFINITION; my 17:50:43 "gap" is narrowed accordingly"** (the ruling after 17:53), in full:

> Verified at origin/main: 03:272-274's worked example declares s_office (risk_premium_minor × decimal factors) as result_type money_minor; FR-248 (03:155) and RL-1329's note (03:483) carry unrounded per-rung values. So a fractional value under a money_minor declaration on an EXPRESSION is the spec's design, not a defect. The predicate and the count (28 in 18 files, including the demo's examples/fremtpl2/model.py:341) are accepted as stated in the plan.
> RULING: (r) as a DEFINITION. The FD 9549-fix RL's FR-227 T-text states: "money_minor on an expression step is a unit (minor units) carrying an exact decimal that may be fractional; only an output step's rounding makes it an integer (FR-226, FR-248)." No OQ. (p) and (q) are recorded with their costs: (q) breaks 28 including the demo and 03's example; (p) contradicts FR-248.
> My 17:50:43 item 2 is NARROWED, not withdrawn: the SERVED form (a money_minor expression → a non-money output, serving 49.5) is the defect, and it is CLOSED by 17:36:28's "OUT of money_minor only into money_minor" rule. PL 9521 adds the red proving it is refused at save (D1). FD 9549 @68a98d6a's amendment says so in those terms: the served half is closed by the fix, and the unserved half is by design under the definition.

## Ruled

All by the maintainer (by delegation), in the entries above. This record states them.

1. **FD 9549's disposition is (a), narrowed: `money_minor` is closed both ways at save**
   (17:36:28, item 2). Out of `money_minor`: only into `money_minor`, for every producer.
   Into `money_minor`: from `money_minor`, or from `decimal` at an output step only (FR-226).
   `relativity`, `percentage` and `count` into `money_minor` are refused. → **T1.**
2. **OQ 9556 is A1 + B3** (17:42:06). A1: `int` → `money_minor` is refused at save; a pence
   integer is declared money by an explicit `money_minor`-typed expression step. B3: widening
   only — `int`, `count`, `relativity` and `percentage` → `decimal`, and `count` → `int`; every
   other non-money pair is refused. The sweep runs before the reds, and a hit is a STOP, not an
   automatic A3. The real-time `/score` coercion is read first. → **T2.**
3. **PL 9521 DP-1 is (ii)** (17:47:06 item 2, as answered at 17:50:43 item 1). A sub-graph
   port carries money as `decimal`; only an output step makes `money_minor`. (a)'s refusal at
   the port stands, `test_rating_compile.py:389` flips, and the 17:47:06 mechanism condition
   is discharged by (ii). **(iii) is refused** — a second rounding point is what FR-226
   excludes. **(i) is not adopted**: the 17:50:43 entry adopts (ii) and refuses only (iii) by
   name. (i) was "admit `decimal` → `money_minor` at a port; the parent's output step rounds
   after inlining" — source: the planner's STOP report as relayed to the maintainer (by
   delegation) before 17:50:43, in the lead's wording; this record has not read the report
   itself. → **T3.**
4. **A-2's control is changed pre-mint** (17:49:25 item 1). #1178 item 15's control becomes a
   `decimal` `model_call` into a **`decimal`** output, legal under B3. This supersedes the
   second-merger flip of 17:47:06 item 4 for that control; PL 9521 names the change and carries
   no flip line for it. The `/score` vs batch comparison is PL 9521's read-only Task 1 Step 1a,
   with the entry's three branches (differ → a separate finding (b); agree and no stored
   refused pair → (c), a residue in FD 9549; a stored refused pair → STOP). **The first branch
   applies**: the 17:52:50 auditor confirmed a divergence, filed as FD 9513 (#1204), which the
   maintainer (by delegation) accepted at 17:58:45 as its own finding with its own fix slice.
   So PL 9521's Step 1a **cites FD 9513** instead of discovering the divergence (17:52:50:
   "PL 9521 Step 1a then CITES the FD instead of discovering it"), and the `score.py` fix is
   FD 9513's slice's — SL 9511 / PL 9509 (working ids, the lead's reservation) — not
   PL 9521's.
5. **The `money_minor`-declared expression DP (PL 9521 DP-2) is (r), closed by definition**
   (17:54:12). No OQ. The served half — a `money_minor` expression into a non-money output —
   is closed by item 1's OUT rule, with PL 9521's red D1. The unserved half — a fractional
   value under a `money_minor` declaration on an expression — is by design (FR-248,
   `RL-1329`, 03:155, 03:483; 03:272-274). → **T4.**

## (p) and (q), recorded with their costs

The count is PL 9521's, DP-2 row, at #1202 head `148892d6`, taken at `5fe56b87`. Its
predicate, verbatim from the plan's source:

```
git grep -n -E '"result_type"\s*:\s*"money_minor"\|result_type[^,)\n]*=\s*"money_minor"\|result_type:\s*money_minor' 5fe56b87 -- . ':!docs'
```

The `\|` is the Markdown table's escape for `|`, because the predicate sits in a table cell.
Run as written in a shell it matches **0** lines. Run with each `\|` read as `|`, this record
measured **29 lines in 18 files** at `5fe56b87`: the plan's 28 declarations plus its one
assertion (`packages/model-schema/tests/test_rating_algorithm.py:146`). The plan's figure
holds under that reading.

- **(p)** — a run-time integrality refusal of a non-integer value under a `money_minor`
  declaration. **Cost:** it contradicts FR-248 as amended by `RL-1329` (03:155), whose rungs
  carry their unrounded exact decimal in minor units, and it breaks the fractional-by-design
  sites the plan lists, 03's own `s_office` example among the shapes it would refuse.
  **Not adopted.**
- **(q)** — refuse `result_type` `money_minor` on expression steps. **Cost:** all 28
  declarations, including the G2 demo seed `examples/fremtpl2/model.py:341`, the three bench
  scripts, and 03's worked example (03:272-274). **Not adopted.**

## The spec texts

**Anchor**, in `docs/specs/03-rating-engine.md`, `grep -cF` = **1** at `5fe56b87`:

```
| **FR-227** | Every step declares its result type, and type compatibility is checked at save time. A monetary result must be `decimal` or `money_minor` (R2). |
```

The texts go **inside that row, after "(R2)." and before the closing ` |`**, in the order
given. Both forms below carry the same rules; **the maintainer picks one.** The decision-maker
recommends **Form A**: one ruling gives one dated amendment, as `RL-1343` gave FR-214, and
four parentheticals on a one-sentence row would read as four separate changes. Form B is
given because the brief asks for T1 to T4 by name. At application, `RL 9512` reads as the
minted id, and the date is that of the applying commit.

### Form A — one dated amendment (recommended)

```
 *(Amended 2026-10-05, `RL 9512` (FD 9549, OQ 9556): **`money_minor` is closed both ways at save.** A `money_minor` value flows only into a `money_minor` slot, whatever step produces it; into `decimal`, `relativity`, `percentage`, `count` or `int` it is refused. A `money_minor` slot accepts `money_minor`, or `decimal` at an `output` step only, where the step's declared rounding (FR-226) makes the integer; `int`, `relativity`, `percentage` and `count` into `money_minor` are refused. A pence integer is declared money by an explicit `expression` step whose `result_type` is `money_minor`. **Among the other numeric types, only widening is admitted:** `int`, `count`, `relativity` and `percentage` into `decimal`, and `count` into `int`. Every other pair is refused, including `relativity` to `percentage` either way and `decimal` into `int`, `count`, `relativity` or `percentage`. **Sub-graphs:** a sub-graph port carries money as decimal; money_minor is produced only at an output step. A `decimal` producer into a `money_minor` output port is refused, and the mounting algorithm's output step rounds the value once. **Expressions:** money_minor on an expression step is a unit (minor units) carrying an exact decimal that may be fractional; only an output step's rounding makes it an integer (FR-226, FR-248).)*
```

### Form B — four dated amendments, T1 to T4

Inserted in this order at the same position; each starts with one space.

**T1** — `money_minor` closed both ways at save, with the output-step exception:

```
 *(Amended 2026-10-05, `RL 9512` (FD 9549), T1: **`money_minor` is closed both ways at save.** A `money_minor` value flows only into a `money_minor` slot, whatever step produces it; into `decimal`, `relativity`, `percentage`, `count` or `int` it is refused. A `money_minor` slot accepts `money_minor`, or `decimal` at an `output` step only, where the step's declared rounding (FR-226) makes the integer; `relativity`, `percentage` and `count` into `money_minor` are refused.)*
```

**T2** — the numeric widening rule (A1 + B3):

```
 *(Amended 2026-10-05, `RL 9512` (OQ 9556), T2: `int` into `money_minor` is refused; a pence integer is declared money by an explicit `expression` step whose `result_type` is `money_minor`. **Among the other numeric types, only widening is admitted:** `int`, `count`, `relativity` and `percentage` into `decimal`, and `count` into `int`. Every other pair is refused, including `relativity` to `percentage` either way and `decimal` into `int`, `count`, `relativity` or `percentage`.)*
```

**T3** — sub-graph ports (DP-1 (ii)):

```
 *(Amended 2026-10-05, `RL 9512` (FD 9549), T3: a sub-graph port carries money as decimal; money_minor is produced only at an output step. A `decimal` producer into a `money_minor` output port is refused, and the mounting algorithm's output step rounds the value once.)*
```

**T4** — the (r) definition, verbatim as ruled at 17:54:12:

```
 *(Amended 2026-10-05, `RL 9512` (FD 9549), T4: money_minor on an expression step is a unit (minor units) carrying an exact decimal that may be fractional; only an output step's rounding makes it an integer (FR-226, FR-248).)*
```

The quoted sentences of T3 and T4 are the entries' words, byte for byte, without code marks,
so that a `grep -F` of the entry's quotation finds them in 03 after application.

## What it obliges

- **PL 9521 (#1202), Task 5**, applies the chosen form byte for byte under `spec-change` and
  runs `python3 scripts/audit-docs.py`. Its activation need for this record (need 5) holds at
  this record's mint.
- **PL 9521's reds** include one per refused direction of T1 and T2, D1 (a `money_minor`
  expression into a non-money output, refused at save), the new port red with `:389` flipped
  and `:388` kept in a renamed test (T3), and the A-control: a `decimal` port into the parent's
  `money_minor` output step saves and rounds once.
- **PL 9521's sweep runs before its reds**; a committed algorithm, fixture or seed that uses a
  refused pair is a STOP to the maintainer (by delegation) with its `file:line`, never a
  loosened rule.
- **PL 9597 (A-2, #1178)** carries item 15's control as a `decimal` `model_call` into a
  `decimal` output, changed before its mint.
- **FD 9549 (#1197)**'s amendment states the served half as closed by the fix and the
  unserved half as by design under T4's definition.
- **PL 9521's Task 1 Step 1a** cites FD 9513 (#1204, head `0303d0bf` when read) for the
  `/score` vs batch divergence, and carries no `score.py` edit and no
  `test_score_and_batch_serve_a_pre_fix_pair_alike` red; both belong to FD 9513's slice.

## What this record does not decide

- **The refusal's error code.** The entries do not name one, and the texts do not either:
  a refused pair is refused by FR-227's existing save-time check, with whatever code that
  check gives at the applying tree.
- **FD 9513's fix.** Its severity, reds and type DP are the 17:58:45 entry's and its own
  plan's (PL 9509); this record only names the hand-off (Ruled, item 4).
- **A new input type** (A4) and any run-time integrality check: neither is taken.
- **The mint order** of this record against FD 9549 and PL 9521: the lead's.

## Acceptance — the violation that must become detectable

The violation: **a value changes its unit — into or out of minor-unit money, or between two
non-money numeric units — by a declaration alone, with no output step's rounding.** Each test
is shown failing on deliberately broken input, in PL 9521.

- **OUT of `money_minor`.** For each of `decimal`, `relativity`, `percentage`, `count` and
  `int`, an algorithm whose `money_minor` producer feeds that declared output is refused at
  save, for every producer whose type is known at save. With
  `_compatible` admitting any numeric pair (as at `5fe56b87`), each red passes the save.
- **INTO `money_minor`.** `int`, `relativity`, `percentage` and `count` into `money_minor` are
  refused; `decimal` into `money_minor` saves at an output step and is refused elsewhere.
- **D1, the served half.** A `money_minor` expression yielding 49.5 into a non-money output is
  refused at save, never served as `49.5`.
- **Widening.** Each of the five admitted widenings saves; each other non-money pair is
  refused, `relativity` ↔ `percentage` included.
- **The port.** A `decimal` producer into a `money_minor` sub-graph output port is refused;
  a `decimal` port into the parent's `money_minor` output step saves, and the scored value is
  rounded once, equal to a hand-computed figure.
- **T4 holds.** 03's `s_office` shape (a `money_minor` expression over decimal factors) still
  saves and scores, and its unrounded rung equals the exact product. A run-time integrality
  check introduced on it makes this test fail.
- **The sweep.** No committed algorithm, fixture or seed newly fails under the rule.

Drafted as working id 9512.
