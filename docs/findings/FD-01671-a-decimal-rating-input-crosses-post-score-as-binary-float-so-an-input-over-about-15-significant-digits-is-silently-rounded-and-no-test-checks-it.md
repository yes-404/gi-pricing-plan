---
id: FD-1671
family: finding
title: A decimal Rating Input crosses POST /score as binary float, so an input over about 15 significant digits is silently rounded and no test checks it
status: active
created: 2026-10-12
owner: auditor
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
corrected_by: []
relates: [WK-1178, SL-1548, SL-2118, FR-213, FR-214, FR-244, FR-273, OQ-1672, RL-1343]
---

# FD-1671 — where a decimal Rating Input becomes a float

*(Minted 2026-10-12 as FD-1671 from working id 9872, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

Found via SL-1548 (WK-675 Slice 6), whose ledger cites it. Filed from the lead's brief of 2026-10-12 and the maintainer's (by delegation) entry "2026-10-12 03:04:43 BST — FD 9872: LOW (not MEDIUM), owner WK-1178; the remedy as proposed CANNOT detect the loss, so it is corrected; plus an OQ on the input wire form" (`to-lead.md`, a local channel file, cited by header). Every line below was re-read at `origin/main` `fc4401dcad789692f79f6c3ffc058c1c3921b7b9` on 2026-10-12.

## Evidence

The hops, in order:

- `backend/src/app/api/score.py:390-391`: the route takes `ctx: QuoteContext` and FastAPI's default JSON parse produces `float64` for a JSON number. `git grep -n parse_float -- backend/src` prints no hit: there is no `parse_float` and no custom decoder.
- `packages/model-schema/src/model_schema/scoring.py:109`: `QuoteContext.inputs` is `dict[str, object]`, with no validator.
- `packages/pricing-core/src/pricing_core/rating/score.py:353` accepts `int`, `float` or `Decimal` (and refuses `bool`). `_as_decimal` (`:321-322`) is used only for the `min`/`max` check (`:380`) and its result is discarded.
- `score.py:955-962` builds `context` from `**ctx.inputs` and passes the raw value to `bundle.decision.async_evaluate`.
- The ZEN binding refuses `Decimal` (FR-244), so the engine evaluates in binary float whatever the parser does.

An input with more than about 15 significant digits is therefore rounded without any signal. The 15-digit figure is **measured** for handler outputs (`LG-1587` lines 67 and 82) and **inferred** for inputs. No test checks the exactness of a decimal input. Money is unaffected: it crosses as integer minor units (FR-273).

## Finding

**Severity LOW (the maintainer's (by delegation), entry "2026-10-12 03:04:43 BST"; not MEDIUM).** Three reasons: (1) past the parse the engine evaluates in binary float by ruled design, so a decimal input over 15 significant digits cannot survive evaluation whatever the parser does; (2) realistic rating factors do not carry more than 15 significant digits; (3) money is integers. It is filed because the alteration is **silent and untested**.

## Disposition

**Owner: WK-1178.** **The remedy must be this, and not the obvious one.** After FastAPI's default parse the original text is gone, so a check of the form "does the float survive a round trip" compares the float with itself and can never fire: it is green by construction. A loud `INPUT_CONTRACT_VIOLATION` needs a **Decimal-preserving parse**: `parse_float=Decimal` on the request body, or reading the raw body for the decimal-typed fields. A test that sends 15 or fewer significant digits and asserts exactness is a **guard**, labelled as such, not a red-first test. Whether the input wire form should change to a JSON string, symmetric with FR-214's decimal outputs, is the open question `OQ-1672`, not decided here. Event that next confirms or discharges it: a merged slice with a Decimal-preserving parse and a test that sends a 17-digit decimal input and is refused (red on `fc4401dc`). Filed by the executor from the entry, 2026-10-12.

*(Dated line, 2026-11-05, docs batch 11, by the auditor, on to-lead "2026-11-05 09:51:53 GMT" (triage b28ba8e9454c accepted as the proposal of record): carried, owner WK-1178, discharge event the P3 plan review; LOW, slice over 1 h, under the 09:40:57 criteria.)*

*(Dated line, 2026-11-09, docs batch 33, by the auditor, on `to-lead` "2026-11-09 23:29:42 GMT" (2): owner P3-C, as its FIRST act, replacing WK-1178, which closes with P2. Severity LOW on record; probe first; money-rule exposure unproven (`to-lead` "2026-11-09 23:38:05 GMT": not re-rated; LOW stands on the record's reason: past the parse the engine evaluates in binary float by ruled design, FR-244, so the parse adds no loss the rating path does not already admit). The 23:29:42 words "a §7 money-rule risk" are the reason for its ORDER (P3-C's first act) and for naming it in the P2 close line, not a severity. The first act's FIRST STEP is the probe: a Rating Input over 15 significant digits through `POST /score` against the same input as Decimal in pricing-core, the priced result compared to the minor unit; the rating is then confirmed LOW or raised by a dated line on the probe's result, never on words. Listed by name in the P2 close line.)*

*(Dated line, 2026-11-13 19:53:34 GMT, on the maintainer's `to-lead` entry "2026-11-13 19:53:34 GMT — Maintainer: RULINGS R1–R3" (R2): **severity MEDIUM**; the LOW of 2026-10-12 above is superseded, its reason (3) kept as written. The probe (`scratch/exec-fd1671p/probe.md`, b1e3ab5aa74b, local and not in the repository) priced `base_minor` 50000 with `factor` 0.82469000000000000002 through `POST /score`: 200, 41234, where the exact Decimal price is 41235, 1 minor unit low, no warning; the same text as a `Decimal` in `pricing-core` is refused `INPUT_CONTRACT_VIOLATION` (FR-273). Reachable only with a 16-or-more-significant-digit Rating Input. **Closed by SL 2118 at its merge:** design (b), the score request bodies read JSON numbers as `Decimal` on `/score` and `/score/compare` only, so the refusal is core's one definition; the red-first and guard tests are `backend/tests/test_score_decimal_input_http.py` and `packages/pricing-core/tests/test_rating_score_decimal_parse_equivalence.py`; `OQ-1672`'s wire form is unchanged, a decimal Rating Input is still a JSON number.)*
