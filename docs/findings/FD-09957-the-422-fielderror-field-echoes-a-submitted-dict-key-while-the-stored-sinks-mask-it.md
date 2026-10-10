---
id: FD-9957
family: finding
title: The 422 FieldError field echoes a submitted dict KEY, where pricing_core.safe_error masks the same key as <key> in every stored or logged sink
status: draft
created: 2026-10-10
owner: auditor
tree: fe0b0627
corrected_by: []
relates: [WK-1178, FD-1589, NFR-499, RL-917, FR-403]
---

# FD-9957 — the 422 `field` echoes a submitted dict KEY

**DRAFT**, filed on `draft/fd-9957-key-echo`, no PR, at the maintainer's ruling (`to-lead.md`,
"2026-10-10 15:52:31 BST — RULINGS on PL 9955 / SL 9956 (FD-1589 row 8 remedy (c),
draft/pl-remedy-c @a8e465be) …", last paragraph): *"The 422 `field` echoing a submitted dict
KEY: YES, one FD row in D8 (owner WK-1178), proposed severity, remedy named. Not in this slice
unless trivially inside its write set."* The weighing it rests on is the entry "2026-10-10
15:37:31 BST — RULING: DP-M2 WITHDRAWN …": a 422 returns to the SAME requester who sent the input.
Every line number is at `origin/main` `fe0b0627`.

This is a sibling of FD-1589 row 8 (`_handle_validation_error`), not a restatement. Row 8 is about
the `message` (`err["msg"]`) and is the subject of PL 9955 / SL 9956. This finding is about the
`field`, which row 8's essay does not mention and remedy (c) does not touch: the DP-5 allow-list
governs which error TYPES render a message, not what the location string contains.

## Evidence

| # | Fact | Where (at `fe0b0627`) |
|---|---|---|
| E1 | The 422 builder joins the pydantic location into `FieldError.field` with no masking: `field=".".join(str(part) for part in err["loc"][1:]) or str(err["loc"][0])`. Only the leading segment (`body`, `query`) is dropped. | `backend/src/app/errors.py:497` (handler `_handle_validation_error`, `:485-513`) |
| E2 | `FieldError.field` is returned to the client in the `application/problem+json` body (`errors=field_errors`, `problem_response`). The handler logs nothing (read, `:485-513`). | `backend/src/app/errors.py:510-513`; `FieldError` at `packages/model-schema/src/model_schema/problem.py:20` |
| E3 | A real request model with a dict field keyed by a caller-chosen string: `DictionaryUpdate.data_dictionary: dict[str, DataDictionaryEntry]` (the route `PUT /datasets/{slug}/dictionary`). Its value model forbids extra keys. Others of the same shape: `DatasetCreate.data_dictionary` (`:135`), `SchemaCorrection.columns: dict[str, str]` (`PATCH /datasets/{slug}/versions/{version}/schema`). | `backend/src/app/api/datasets.py:138-141`, `:135`, `:162-168`, routes `:494-501` and `:751-760`; `DataDictionaryEntry` `extra="forbid"` at `packages/model-schema/src/model_schema/datasets.py:147` |
| E4 | `pricing_core.safe_error` states the hazard in its own docstring: a `ValidationError`'s `loc` "carries the offending KEY of a dict-typed field", and masks it: "a dict key or an extra key becomes `<key>`". | `packages/pricing-core/src/pricing_core/safe_error.py:3-9` and `:17-19` |
| E5 | The masking is `_safe_location`: a part is kept only if it is an int (a list index, as `[n]`) or a field name some loaded Pydantic model declares (`_declared_field_names`, `:77-93`); every other part becomes `<key>`. | `packages/pricing-core/src/pricing_core/safe_error.py:96-101` (used at `:109`) |
| E6 | So the stored and logged sinks are safe and the 422 response is not: the same `loc` is masked in `safe_error_detail` and echoed raw in the 422. | E1 against E5 |
| E7 | The only frontend consumer of `errors[].field` that shows it prints it verbatim (`{{ error.field }}`). | `frontend/src/views/ModelSpecBuilderView.vue:627` |

### Example, by reading (not run)

Request: `PUT /api/v1/datasets/motor/dictionary` with body
`{"data_dictionary": {"Jane Smith DOB 1985-03-04": {"descriptoin": "x"}}}`.

1. `DictionaryUpdate` validates `data_dictionary` as `dict[str, DataDictionaryEntry]`. The entry
   forbids extras, so the misspelt `descriptoin` fails with type `extra_forbidden`.
2. Pydantic's `loc` is `("body", "data_dictionary", "Jane Smith DOB 1985-03-04", "descriptoin")`:
   the dict key is a location part.
3. `errors.py:497` drops `"body"` and joins the rest:
   `field = "data_dictionary.Jane Smith DOB 1985-03-04.descriptoin"`. The 422 returns it.
4. Through `_safe_location` the same `loc` renders `body.<key>.<key>`-style as follows:
   `body` is not a declared field name and also becomes `<key>`, `data_dictionary` is declared and
   stays, the dict key and the extra key become `<key>`. Dropping `body` first, as remedy point 1
   does, gives `data_dictionary.<key>.<key>`.

## Finding

The 422 response puts a caller-chosen dict key into the `field` string, while the module that
exists to keep such keys out of text (NFR-499, RL-917) masks the same key. The two disagree about
the same `loc`.

**Proposed severity: LOW (the auditor proposes; the lead decides)**, the same as FD-1589 row 8 and
for the reason the 15:37:31 entry weighs:

- The value is returned to the requester who sent it. Nothing is stored by this handler (E2: it does not
  log or persist), and no other reader of the response is identified here. NFR-499's harm is input
  reaching a store or another reader; neither is on this path.
- It is a key, never a value the platform holds: a column name or a rating-factor key. A key that
  is itself personal data is possible (a dict keyed by a name, as in the example) but is the
  requester's own.
- It becomes MEDIUM only if a later change logs or stores the 422 body, or relays it to a reader
  other than the sender (a Job error field, an audit row, a shared UI banner). Event that
  raises it: any such change.

## Remedy, named

The 422 builds `field` through the same location masking as `safe_error`: expose the existing
`_safe_location` as a public `pricing_core.safe_error` helper (the backend must not import an
underscore name) and call it at `errors.py:497` in place of the bare join. Three points a
planner must settle, none open to a silent pick:

1. **Query and path parameters.** `_declared_field_names` holds model field names only. A failing
   query parameter (`limit`, `cursor`) is not one, so a naive call would mask it as `<key>` and
   lose the field name FR-403 asks the UI to mark. The helper must mask only locations whose
   first segment is `body`; `query`, `path`, `header` and `cookie` parameter names are declared
   by the route and kept.
2. **UI cost.** E7: the builder view prints `field` verbatim, so `data_dictionary.<key>.<key>`
   replaces the column name an actuary reads today. This is the usability trade the 15:37:31 and
   15:52:31 entries refuse to ship for `msg`, at smaller scale (the location, not the message).
   Whether to accept it, or to keep the key and drop only keys the caller did not declare
   elsewhere, is the lead's DP, to come with the plan.
3. **Placement.** Not in PL 9955's slice. The 422 helper (`errors.py`) is inside its write set,
   but the change alters a rendering the slice's red-first tests and the `ModelSpecBuilderView`
   mock do not cover (DP-4 keeps `msg` byte-identical, not `field`), and point 2 needs a ruling,
   so it is not trivial. Recommend its own row in a later WK-1178 slice, after PL 9955 / SL 9956
   merges, sharing that slice's `errors.py` edit-order.

## The remedy decision — OPEN

The remedy's one open choice is point 2 above, put to the maintainer by the lead in the entry
"2026-10-10 15:56:01 BST — Lead: FD 9957 drafted (the 422 field echoes a submitted dict key) — LOW;
placement: its own later WK-1178 slice; one UX trade-off for your ruling at D8 (not urgent)" in
`from-lead-2026-10-09.md`. **No ruling exists at `e4753e47`; none is assumed here.** The options,
in that entry's words:

- **(a)** mask body-dict keys in the 422 `field` (privacy; the UI loses the column name);
- **(b)** keep the key in the 422 (requester-only exposure) and record the residual;
- **(c)** keep the key only when it is a column the dataset already declares (known names) and mask
  unknown keys.

**The lead leans (c)**, because it keeps the name an actuary reads when it is one the dataset
declared and masks the free text that is the exposure. Placement is ruled: its own later WK-1178
slice, after SL 9956 (PL 9955's slice A) merges, per the 15:52:31 entry's "not in this slice unless
trivially inside its write set". The slice's plan comes to the lead with the choice named as a
decision point; the planner does not pick it.

## Disposition

**Owner: WK-1178** (the 15:52:31 ruling). Decision: `fix before close with an owner: WK-1178`,
severity LOW as proposed. Event that next confirms or discharges it: the ruling on the remedy
decision above (open), then the remedy PR with a test red at its parent that submits a dict key and reads
`field` back.
