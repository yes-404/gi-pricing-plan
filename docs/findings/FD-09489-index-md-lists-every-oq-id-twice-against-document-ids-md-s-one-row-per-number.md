---
id: FD-9489
family: finding
title: INDEX.md lists every OQ id twice, against document-ids.md's one row per number
status: active
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: auditor
tree: a5657fa4520739f182cbea79e0057afeed991ac1
corrected_by: []
relates: [WK-1178]
---

# FD-9489 — `build_corpus` keeps both the `open-questions.md` row and the spec §10 row of every OQ, so `docs/INDEX.md` has two rows for each of 136 ids

**Filed** by auditor-indexdup on the lead's brief of 2026-10-05, working id 9489 (reserved in the lead's `eta.md`),
from the maintainer's (by delegation) follow-up in `to-lead.md`, entry headed "2026-10-05 19:56:53 BST — MERGE-ACK #1133
(lane C pair: RL-1428, PL-1429, SL-1430) @27f4a8f5d36a7d4f2faac467ca4d398a78b73c02; one follow-up on INDEX duplicates"
(a local channel file, so cited by its header). The follow-up read: *"INDEX has 136 duplicate ids, the same on main" is a
claim I have not seen explained* — a read-only check, by design or defect. The lead's verdict on the report: the
source duplication is by design (the mirror rule); the INDEX output is a generator defect against `document-ids.md` :71.
`tree:` is `origin/main` at filing; every measurement below ran at that tree.

## Finding

**Severity: LOW (proposed by the auditor; the lead gives the verdict); owner WK-1178.** At
`a5657fa4520739f182cbea79e0057afeed991ac1`, `docs/INDEX.md` carries two rows for each of 136 OQ ids, 272 rows for 136
numbers, and no other id is repeated. `docs/process/document-ids.md` :71 says "`INDEX.md` has one row per number for
both" (document and row families), :94 says "generated — one row per id, rows and documents alike", and
`scripts/doc-index.py` :1 says "one row per id, rows and documents alike". The generator does not keep that rule for
the one family the specification says is mirrored (`document-ids.md` :43, :98).

It is LOW because nothing resolves wrongly: `Corpus._by_id` (`scripts/doc-index.py` :153-160) is last-wins, so an OQ id
resolves to the spec row, and `audit-docs.py` check 32 and `doc-id.py next` read the set of ids, not the row count. What a
reader gets is two rows for one number with two different titles (the two texts differ for all 136 ids), neither
marked as the mirror of the other. `doc-id.py check`'s `find_duplicate_ids` (`scripts/doc-id.py` :462-486) reads
document headers only, so no gate check sees a repeated row id.

## Evidence

### 1. Three predicates, verbatim, at `a5657fa4520739f182cbea79e0057afeed991ac1`

| # | predicate | count |
|---|---|---|
| P1 (the lead's ad hoc one) | `git show origin/main:docs/INDEX.md \| grep -oE '^\| *\[?[A-Z]{2,3}-[0-9]+' \| sed 's/[\|[ ]//g' \| sort \| uniq -d \| wc -l` | 136 |
| P2 (the id column parsed) | `awk -F'\|' '$2 ~ /^ *[A-Z]+-[0-9]+ *$/ {gsub(/ /,"",$2); c[$2]++} END{n=0;for(k in c) if(c[k]>1)n++; print n}' INDEX.md` | 136 (1566 id rows; 1588 table rows including the header and the id-less reference rows) |
| P3 (the generator's own records, with the path beside the id) | `build_corpus(Path("docs"))` from `scripts/doc-index.py`, records grouped by `header.id`, each record's `path` listed | 136 ids with 2 records, 0 with 3 or more |

P1 is sound here because the id column is plain text. P2 and P3 agree with it.

### 2. Classification (P3's paths)

| class | count |
|---|---|
| same id, different paths: `docs/open-questions.md` plus one spec | 136 (all) |
| same id, same path (a true duplicate) | 0 |
| a repeated id outside the OQ family (FR, NFR, DEP, WK, SL, a document family) | 0 |
| parse artefact of the predicate | 0 |

OQ records per file: `open-questions.md` 136; specs `02` 46, `07` 20, `00` 19, `03` 17, `01` 15, `06` 8, `04` 6,
`05` 5 (sum 136). Every OQ id has both a mirror row and a spec row, and none has one only. The two rows' titles differ for
136 of 136 ids (the spec row is the bold question; the mirror row carries the unbolded text, the `~~` strike and the
`DECIDED` form).

### 3. Mechanism

`build_corpus` (`scripts/doc-index.py` :724-735) appends `scan_bold_id_rows(root / "open-questions.md", root)` and then
`scan_bold_id_rows` of every `specs/*.md`. `render_index` (:1235-1262) writes one row per `Record`, sorted by `_sort_key`
(:1229), and keeps no path. Nothing merges two records of one id. `document-ids.md` :43 gives the OQ row family "`docs/specs/<module>.md`
§10, mirrored in `docs/open-questions.md`", so the second record is expected; the rule at :71 was not carried into the
generator.

## Options (a ruling, so none is chosen here)

| option | change | trade-off |
|---|---|---|
| (a) dedupe in the generator, preferring the spec row | `build_corpus` or `render_index` keeps one record per id for the OQ family; the spec §10 row wins, as `_by_id` already does | Makes the generator say what :71 and :94 say; INDEX shrinks by 136 rows; a regenerated INDEX changes (check 39 is byte-stable against a fresh run, so the INDEX regeneration lands in the same commit). Loses the mirror row from the index; a mirror row that drifts from its spec row is then seen only by the existing §10 mirror check, not by INDEX. |
| (b) amend `document-ids.md` :71 (and :94, and the `doc-index.py` :1 docstring) | say OQ has two rows by design: the spec row and its mirror | No code or INDEX change. Weakens "one row per number" to "one row per number except OQ", the one family where a reader must then know which row is canonical. Needs a dated ruling, and an `RL-` since :71 is a governed rule. |
| (c) add a `path` column to INDEX | `render_index` writes the record's `path`, so a repeated id is explained by its row | Keeps both rows and makes them distinguishable; also gives every id its resolving file, which :71 says an id has ("resolves to a file and an anchor"). Widens a generated table of 1588 rows by one column and changes every row, so a large diff and a one-time churn for anyone reading INDEX by column. Does not make the row count one per number. |

**Recommendation (the auditor's, for the lead and the maintainer):** (a). :71 and :94 are the stated contract, the code is
the side that disagrees, and one resolving row per id is what check 32 and `_by_id` already assume. (c) is a reasonable
second step if a path per id is wanted, and it is independent of (a). (b) is the choice if the maintainer wants the mirror
visible in INDEX. This is a ruling on the contract, not a code decision, so the choice stays open.

## Disposition

Proposed by the auditor; the lead gives the verdict. **Carry forward with an owner: WK-1178 (proposed; the lead's verdict).** Event that next confirms or discharges it: a
dated ruling choosing (a), (b) or (c), and the PR that implements it with `doc-index.py --check` green at its tree.
Claims in this essay are about `a5657fa4520739f182cbea79e0057afeed991ac1` and were re-read there; nothing here was run
against any other tree.
