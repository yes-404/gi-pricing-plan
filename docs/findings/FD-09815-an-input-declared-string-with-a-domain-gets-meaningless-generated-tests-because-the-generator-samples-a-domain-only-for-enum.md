---
id: FD-9815
family: finding
title: An algorithm input declared "string" with a "domain" gets meaningless generated property tests, because generate_contexts samples a domain only for enum
status: active
created: 2026-10-11
owner: auditor
tree: 02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a
corrected_by: []
relates: [WK-1178, SL-1526]
---

# FD-9815 — a `string` input with a `domain` is sampled as arbitrary text

**Working id 9815, to be minted in the D11 batch.** Filed at the lead's entry "2026-10-11 11:40:34 BST — SL-1526 cause = a
declaration defect: OPTION 1 RULED (declare the five categoricals `enum`); it is NOT under my STOP; conditions on the hash and
prices; FD LOW for the latent trap", item 4. Lines are at `origin/main` `02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a`.

## Evidence

- `packages/pricing-core/src/pricing_core/rating/testing.py:137-140`: only `RatingInputType.ENUM` samples the declared domain
  (`st.sampled_from(field.domain)`). A `string` falls through to `:146-149`: `st.from_regex(field.pattern)` if a pattern is
  declared, else `st.text(alphabet=letters+digits, min_size=1, max_size=12)`. A `domain` on a `string` is ignored.
- SL-1526 (LG 9966; in-process run, `handover/sl1526-regate/inproc.out`, as the lead read it at 11:40:34): its algorithm declared
  five categorical inputs as `"type": "string"` plus `"domain"`. The golden bases pass all three properties (base 1 veh_age:
  25000 → 27629 → 32101); **all 25 generated contexts fail**, because the random text matches no rate-table key and the table
  lookup misses (`on_miss: "error"`). SL-1526 fixes its own instance by declaring the five inputs `enum` (ruled 11:40:34 item 1;
  accepted at 11:43:32: 0/25 → 25/25 generated contexts pass).

## Finding

The property suite (FR-261) for such an algorithm reports failures that say nothing about the algorithm. Nothing refuses the
declaration, so any author who writes `string` + `domain` gets a red suite with no pointer to the cause.

**Severity (proposed by the auditor): LOW.** The reason: it costs diagnosis time and a gate re-run, nothing is mispriced, and the
only known instance is repaired by its own slice.

## Remedy options (decided later; none is taken here)

(i) the generator honours `domain` whatever the input type; (ii) a save-time refusal of `string` + `domain`; (iii) both.
Option (i) is a shared pricing-core change, which 11:40:34 item 3 declined for SL-1526 ("not now").

## Disposition

**Owner: WK-1178.** Decision: `fix before close with an owner: WK-1178`, or accept at the P2 close. Event that next
confirms or discharges it: a decision between (i)–(iii) and its slice. Filed by the auditor, 2026-10-11; the lead gives the verdict.
