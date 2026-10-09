---
id: FD-9460
family: finding
title: An empty double-quoted literal in any tracked file crashes test_rating_committed_strings instead of being checked (group(2) or group(3) turns "" into None)
status: active
created: 2026-10-08
owner: auditor
tree: d85cf85455fcb7ddc6d9c207ee5e5002ed667719
corrected_by: []
relates: [WK-1178, FR-244, LG-9476]
---

# FD-9460 — An empty double-quoted literal crashes test_rating_committed_strings

## Finding

`packages/pricing-core/tests/test_rating_committed_strings.py` (FR-244's sweep: every authored
`expr` / `condition` / `key_expr` / `clamp_bounds` string in a tracked file is accepted by the
engine or is a declared negative) builds its set of strings with

- `match.group(2) or match.group(3)` (`:110`, at `d85cf854`), and
- `inner.group(1) or inner.group(2)` (`:113`, the clamp bounds).

Each pair is (double-quoted alternative, single-quoted alternative). A **double-quoted empty**
literal matches the first alternative with `group(2) == ""`, which is falsy, so `or` falls
through to `group(3)`, which is `None` (that alternative did not participate). The set then
holds `None` where a `str` belongs, and the test dies on it instead of checking it:

- `_codes(None)` reaches `_check_determinism` (`pricing_core/rating/compile.py:262`),
  `text.lower()` → `AttributeError: 'NoneType' object has no attribute 'lower'`.
- For the clamp-bound form, `sorted(committed)` compares `None` with a `str`:
  `TypeError: '<' not supported between instances of 'str' and 'NoneType'`.

The single-quoted empty literal does **not** crash (`None or ''` is `''`); it reaches the
assertion and is reported as unexplained (see Evidence). So the crash is the double-quoted
form, not "any empty literal".

**Who it blocked.** SL-1477 (S2, #1245): `DagDesigner.vue`'s `blank()` wrote `expr: ""` and
`condition: ""`; the S2 first gate failed on this test; the slice worked around it with a
named empty constant (LG-9476, "After the first gate" section's gate list, item (ii), which
calls it an "FD candidate"). The test is outside that slice's write set.

**Why it is an FD and not a backlog row.** The entry headed "2026-10-08 14:29:15 BST — S2
(#1245): re-gate ACCEPTED as required; …" (`~/gi-pricing-plan.local/channel/to-lead.md`, item 3)
rules: *"FD CANDIDATE: FILED as an FD, LOW, owner WK-1178. It is a test that crashes instead of
checking, and it blocked work today (the S2 gate), so even read as process it meets L3's valve
limb (ii)."* The L3 rule is item 4 (T5) of the entry headed "2026-10-08 13:11:28 BST — CONTRIBUTING.md (draft/contributing @67c73a32) REVIEWED: …" in the same file: until the P2 exit demo a process finding is a backlog row "unless it lets a wrong merge, a wrong number or data loss through or blocks work".

## Evidence

Broken-input reproduction, in a scratch git repository (`/tmp/fd9460-scratch.*`, 2026-10-08)
holding the test file at its path and one tracked fixture; the repository's own interpreter
(`.venv/bin/python`, pytest 9.1.1):

```
$ printf 'expr: ""\n' > fixture.yaml; git add -A
$ .venv/bin/python -m pytest -q -p no:cacheprovider --rootdir=<scratch> \
    <scratch>/packages/pricing-core/tests/test_rating_committed_strings.py \
    -k every_committed_string_is_accepted
E   AttributeError: 'NoneType' object has no attribute 'lower'
packages/pricing-core/src/pricing_core/rating/compile.py:262: AttributeError
FAILED ...::test_every_committed_string_is_accepted_or_a_declared_negative
  - AttributeError: 'NoneType' object has no attribute 'lower'      (1 failed, 3 deselected)
```

Variants, same scratch repository, same command:

| fixture line | result |
|---|---|
| `expr: ""` | `AttributeError: 'NoneType' object has no attribute 'lower'` |
| `expr: ''` | no crash; `AssertionError` (reported as unexplained) |
| `clamp_bounds: {"min": "", "max": "1"}` | `TypeError: '<' not supported between instances of 'str' and 'NoneType'` |

What the engine says of the empty string, so the follow-on in the Disposition is real
(`STRING_CHECKS` applied to `''`): the first four checks return `None`; the fifth returns
`('EXPRESSION_INVALID_VOCABULARY', '… parserError … Unexpected end of unary expression at (0, 0)')`.

Not reproduced from the S2 gate log: `~/.cache/fps-harness/gate-out.txt` is the fps run's
output and holds no pytest text; the gate failure is as LG-9476 records it, not independently
re-read here.

## Disposition

LOW; owner WK-1178 (the lead's ruling, quoted above). Open.

**Remedy, described and not applied** (an add-on to the next WK-1178 money/contract slice's write
set, red first): `group(2) if group(2) is not None else group(3)` at both sites. **The
one-line change alone does not meet the ruling's "an empty literal in a fixture file must
pass the test":** it turns the crash into the single-quote row's outcome — the empty string
reaches `_codes('')`, is refused with `EXPRESSION_INVALID_VOCABULARY`, and the test fails as
"unexplained". Making it pass is a second, open choice for the slice: (a) the extractor skips
an empty literal, because a blank is a placeholder and not an authored expression (recommended:
one condition, no new declared negative); or (b) declare `''` in `_NEGATIVES` with the
`EXPRESSION_INVALID_VOCABULARY` code and the test that asserts it. The red-first tests are the
three fixture lines of the table above, in a temporary tracked file, each required to pass.
