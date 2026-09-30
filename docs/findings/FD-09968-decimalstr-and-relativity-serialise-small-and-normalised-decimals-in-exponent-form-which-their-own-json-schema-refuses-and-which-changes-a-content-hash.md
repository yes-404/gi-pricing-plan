---
id: FD-9968
family: finding
title: DecimalStr and Relativity serialise small and normalised decimals in exponent form, which their own JSON Schema refuses, and the spelling changes a content hash
status: active
created: 2026-09-30
owner: auditor
tree: 32f3fa92afad81d1be611b21ae16ff35211eded8
corrected_by: []
relates: [WK-1178, FR-10, FR-451]
---

# FD-9968 — `DecimalStr` serialises exponent form and preserves spelling, so a value can violate its own schema and change a hash

## Finding

**Severity: MEDIUM**, ruled by the maintainer (see *Severity*). **Proposed by the auditor; the disposition is the
lead's.** FD-9968 is a working id, minted at the records PR.

`model_schema.money.DecimalStr` (`packages/model-schema/src/model_schema/money.py:85-91`) and `Relativity`
(`:94-99`) serialise with `PlainSerializer(str, …)`, and `str()` of a `Decimal` uses exponent form outside
a plain-positional range. Two consequences, both measured at `origin/main`
`32f3fa92afad81d1be611b21ae16ff35211eded8` (evidence 1 to 3):

1. **A value the type accepts serialises to a string the type's own JSON Schema refuses.** The generated schema
   for both types is `{"type": "string", "pattern": "^-?[0-9]+(\.[0-9]+)?$"}` (`_DecimalStrSchema`,
   `money.py:46-58`; the pattern is the type's contract: "Exact decimal as a string; never a binary float
   (FR-10)"). `Decimal("0.0000001")` serialises as `"1E-7"`, `Decimal("0.00000000000000000000000000012")` as
   `"1.2E-28"`, and any decimal with a positive exponent, such as `Decimal(100).normalize()`, as `"1E+2"`: none
   matches the pattern. The value round-trips in Python (`Decimal("1E-7")` parses), so nothing fails in-process;
   a consumer that validates against the published contract does.
2. **The serialised spelling follows the input's spelling, not the value.** `"10"` and `"1E+1"` are equal
   decimals and serialise as `"10"` and `"1E+1"`; `"66000.440"` stays `"66000.440"`. So two value-equal contents
   have different bytes, and **any hash taken over the dump differs**. Evidence 3 shows it on the one content
   hash that includes a `DecimalStr`.

`dm-eh-s3`'s RL 9963 (working id 9963, part 1a) found it while ruling the premium ladder and recorded it as an
observation "for the lead", and chose a **new** `PositionalDecimalStr` for the ladder's own fields rather than
change `DecimalStr`, because "`DecimalStr` has 23 uses in `model_schema` outside `money.py` … some of them in
content-hashed artifacts. Changing its serialiser would change stored bytes and hashes beyond this slice."
This record measures that.

## Evidence

Run at `origin/main` `32f3fa92afad81d1be611b21ae16ff35211eded8`, 2026-09-30, by the filer, under
`uv run --no-sync python`; the scripts are kept with the evidence.

**1. The reproduction** (`decstr_repro.py`; the first block is RL 9963's own snippet). Output, verbatim:

```text
1. the RL 9963 part 1a snippet, at this tree:
   '0.0000001'                          -> {"a":"1E-7","r":"1E-7"}
   '0.00000000000000000000000000012'    -> {"a":"1.2E-28","r":"1.2E-28"}
   '10'                                 -> {"a":"10","r":"10"}
   '1E+1'                               -> {"a":"1E+1","r":"1E+1"}
   '66000.440'                          -> {"a":"66000.440","r":"66000.440"}

2. the type's own JSON Schema pattern: ^-?[0-9]+(\.[0-9]+)?$
   re.fullmatch(pattern, '1E-7') -> False
   re.fullmatch(pattern, '0.0000001') -> True
   re.fullmatch(pattern, '1E+1') -> False
   re.fullmatch(pattern, '10') -> True

3. equal values, different bytes: Decimal('10') == Decimal('1E+1'): True | dumps: {"a":"10","r":"1"} vs {"a":"1E+1","r":"1"}
   and arithmetic results: Decimal(100).normalize() -> 1E+2 | dumps: {"a":"1E+2","r":"1"}
```

**2. The uses.** `DecimalStr` is the type of **13 fields in 11 models** (`git grep -n -E ":\s*(tuple\[|list\[)?(DecimalStr|Relativity)\b"
-- packages/model-schema/src`, then `grep -v money.py`: **13 lines**, rerun at `7a81cf27`; without the `\b` it is 14, because `comparison.py:196`, `tuple[RelativityDifference, …]`, matches through the `Relativity` prefix): `DoubleLiftBin.exposure_years` (`comparison.py:136`),
`VersionTotals.exposure_years` (`datasets.py:281`), `AeCell.exposure_years` (`diagnostics.py:93`),
`LiftBin.exposure_years` (`:114`), `BandingMinimums.min_exposure_per_band` (`modelling.py:334`),
`LargeLossTreatment.restoration_loading` and `.loading_factor` (`perils.py:155`, `:165`),
`Reconciliation.tolerance` (`:308`), `Histogram.exposure` (a tuple, `profiles.py:67`), `LevelCount.exposure_years`
(`:110`), `OneWayRow.exposure_years` (`:154`) and `MonotoneInInput.lower` and `.upper` (`regression.py:103-104`).
The 23 in RL 9963 is a line count (`git grep -n "DecimalStr\b"` outside `money.py` also counts imports and the
`__init__` re-export); `Relativity` is declared but is the type of no field. **Where a value feeds a content
hash:** `suite_content_hash` (`regression.py:219`) is `sha256` over
`RegressionSuiteContent.model_dump(mode="json")`, which includes each property's `check`, and `MonotoneInInput`
carries `lower` and `upper`. **These two fields, `MonotoneInInput.lower` and `.upper`, are the only `DecimalStr`
fields in a hash the code computes itself.** `spec_hash` (`backend/src/app/platform/modelling.py:155`,
`SPEC_HASH_VERSION = 11`) hashes `ModelSpec`, which pins a `Banding` by id rather than embedding it, so
`BandingMinimums` is not in it; `bundle_hash` (`compile.py:408`) hashes the graph and the pins, no decimals; the
blob store's digests are over bytes and none of the JSON payloads it stores carries these fields (`model_handlers.py:534`,
`:540` store a booster and a covariance). The `exposure_years` fields are in profile, diagnostics and comparison
artifacts persisted as `jsonb` rows, not hashed.

**3. A content hash that changes with the spelling.** `decstr_repro.py` builds a `RegressionSuiteContent` whose
one property is `MonotoneInInput(lower=…)` and takes `suite_content_hash`. Output, verbatim:

```text
4. a content hash that changes with the spelling (RegressionSuiteContent, `suite_content_hash`, regression.py:219):
   lower='10'           -> dumped '10'           hash sha256:b7986380b94f4741...
   lower='1E+1'         -> dumped '1E+1'         hash sha256:60852424a1223d86...
   lower='0.0000001'    -> dumped '1E-7'         hash sha256:62e4bb1541ed8b41...
   lower='0.00000010'   -> dumped '1.0E-7'       hash sha256:f4201a88382f83b3...
```

Equal values (`10` and `1E+1`) give different suite hashes. The suite hash is pinned as evidence
(`evidence.golden_quotes.suite_content_hash`, `backend/src/app/platform/rating_versions.py:612`, `:639`), so a suite
re-created from the same values with a different spelling would compare as a different suite. That fails loudly
(a hash mismatch), not silently, and needs a `lower` or `upper` an actuary typed in exponent or padded form.

**4. The measured count of committed artifacts holding an exponent-form value.**
*Predicate, verbatim* (`decexp.py`, `python3 decexp.py 32f3fa92afad81d1be611b21ae16ff35211eded8`): over the
tracked blobs of that tree (`git ls-tree -r -z --name-only`, then `git show <ref>:<path>`, so the working tree and
this record's own additions are never read; 1901 files, all decodable as UTF-8), the Python regular expressions below,
the first over any quoted string in the shape `DecimalStr` serialises, the second requiring a `DecimalStr` field name
as its key:

```python
Q = re.compile(r"""(?:"|')(-?\d+(?:\.\d+)?[eE][+-]?\d+)(?:"|')""")
FIELDS = ("exposure_years", "min_exposure_per_band", "restoration_loading", "loading_factor", "tolerance", "exposure", "lower", "upper", "factor")
KEYED = re.compile(r"""(?:"|')(%s)(?:"|')\s*:\s*\[?\s*(?:"|')(-?\d+(?:\.\d+)?[eE][+-]?\d+)(?:"|')""" % "|".join(FIELDS))
```

| Corpus | Result |
|---|---|
| All 1901 tracked files | **7** quoted exponent-form strings in **5** files |
| … in `examples/`, fixtures, golden files, `docs/contracts/` or any JSON, YAML or CSV file | **0** |
| … keyed to a `DecimalStr` field name | **0** |

The 7 are not stored values: `packages/model-schema/tests/test_money.py:78` (`float("1e-7")`, a float the type
must refuse), `packages/pricing-core/tests/test_objectives.py:285` (an assertion that an error detail contains `1e-04`),
`packages/pricing-core/tests/test_rate_table_operations.py:324` (`Decimal("1e-9")` as an `approx` tolerance),
`tests/test_watcher_runtime_state.py:218` and `:243` (`"1407e09"`, an id) and two prose mentions of `1e3` in
`docs/rulings/RL-01322-*.md`. **So no committed artifact holds an exponent-form `DecimalStr` value**, and no
committed file is a content-hashed artifact carrying a `DecimalStr` field (`sha256:` appears only in
`.github/workflows/python.yml`, `docs/process/delivery-process.core.json` and `docs/specs/03-rating-engine.md`).
*Population, so a 0 is not read from an empty corpus:* a second predicate (`decexp2.py`, the same `git show` reading, quoted
plain-decimal strings under a `DecimalStr` field name), finds **34** in tracked files (13 `exposure_years`, 10 `lower`, 8 `upper`, 2
`min_exposure_per_band`, 1 `tolerance`), in tests and specification examples, none in exponent form.
*Positive control:* `decexp_ctl.py` builds a scratch git repository (committed, then read by the same script at `HEAD`) with `{"lower": "1E-7", "upper": "0.5"}`,
`{"exposure_years": "1.2E-28"}` and `{"lower": "0.0000001", "upper": "10", "x": "1E+1"}`: the predicate counts **3**
exponent strings in 3 files (including the positive-exponent `1E+1`), and **2** keyed to a field name; the plain
`0.0000001` and `10` are not counted. The scratch directory was removed.

*The population predicate, `decexp2.py`, verbatim:*

```python
"""Population: quoted plain-decimal strings under a DecimalStr field name, in the tracked blobs of a git ref."""
import collections, os, re, subprocess, sys
ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
FIELDS = ("exposure_years", "min_exposure_per_band", "restoration_loading", "loading_factor", "tolerance", "exposure", "lower", "upper")
ANY = re.compile(r"""(?:"|')(%s)(?:"|')\s*:\s*\[?\s*(?:"|')(-?\d+(?:\.\d+)?)(?:"|')""" % "|".join(FIELDS))
files = [f.decode() for f in subprocess.run(["git", "ls-tree", "-r", "-z", "--name-only", ref], capture_output=True).stdout.split(b"\0") if f]
pop = collections.Counter(); where = collections.Counter()
for f in files:
    try:
        t = subprocess.run(["git", "show", f"{ref}:{f}"], capture_output=True).stdout.decode("utf-8")
    except UnicodeDecodeError:
        continue
    for k, v in ANY.findall(t):
        pop[k] += 1; where[(f.split("/")[0], os.path.splitext(f)[1])] += 1
print("ref", ref, "| quoted plain-decimal values under a DecimalStr field name:", sum(pop.values()), dict(pop))
print("by (top dir, ext):", dict(where))
```

*The driver the control calls, `decexp.py`, verbatim (the control runs it in its scratch repository, so the essay holds both scripts; save this as `/tmp/scan/decexp.py`):*

```python
"""Committed files holding a decimal in exponent form as a quoted string (the shape `DecimalStr` serialises).
Reads the tracked blobs of a git ref (default HEAD), never the working tree."""
import collections, os, re, subprocess, sys
ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
FIELDS = ("exposure_years", "min_exposure_per_band", "restoration_loading", "loading_factor", "tolerance", "exposure", "lower", "upper", "factor")
Q = re.compile(r"""(?:"|')(-?\d+(?:\.\d+)?[eE][+-]?\d+)(?:"|')""")
KEYED = re.compile(r"""(?:"|')(%s)(?:"|')\s*:\s*\[?\s*(?:"|')(-?\d+(?:\.\d+)?[eE][+-]?\d+)(?:"|')""" % "|".join(FIELDS))
files = [f.decode() for f in subprocess.run(["git", "ls-tree", "-r", "-z", "--name-only", ref], capture_output=True).stdout.split(b"\0") if f]
tot = collections.Counter(); byclass = collections.Counter(); hits = []; keyed = []
skipped = 0
for f in files:
    blob = subprocess.run(["git", "show", f"{ref}:{f}"], capture_output=True).stdout
    try:
        text = blob.decode("utf-8")
    except UnicodeDecodeError:
        skipped += 1; continue
    tot["files_scanned"] += 1
    m = Q.findall(text)
    if m:
        ext = os.path.splitext(f)[1].lower() or "(none)"
        byclass[(f.split("/")[0], ext)] += len(m)
        hits.append((f, len(m), sorted(set(m))[:4]))
        tot["quoted_exponent_strings"] += len(m)
    for k in KEYED.findall(text):
        keyed.append((f, k))
print("ref:", ref, subprocess.run(["git", "rev-parse", ref], capture_output=True, text=True).stdout.strip())
print("files scanned:", tot["files_scanned"], "(binary/undecodable skipped:", skipped, ")")
print("quoted exponent-form strings:", tot["quoted_exponent_strings"], "in", len(hits), "files")
print("by (top dir, extension):", dict(byclass))
for h in hits:
    print("  HIT", h)
print("keyed to a DecimalStr field name:", len(keyed))
for k in keyed:
    print("  KEYED", k)
```

*The positive-control script, `decexp_ctl.py`, verbatim:*

```python
import subprocess, sys, os, tempfile, shutil, re
# 1. the file predicate on a planted scratch repo
d = tempfile.mkdtemp(prefix="dctl-")
try:
    subprocess.run(["git", "init", "-q", d], check=True)
    open(d + "/a.json", "w").write('{"lower": "1E-7", "upper": "0.5"}\n')
    open(d + "/b.json", "w").write('{"exposure_years": "1.2E-28"}\n')
    open(d + "/c.json", "w").write('{"lower": "0.0000001", "upper": "10", "x": "1E+1"}\n')
    subprocess.run(["git", "-C", d, "add", "."], check=True)
    subprocess.run(["git", "-C", d, "-c", "user.email=a@b.c", "-c", "user.name=x", "commit", "-qm", "c"], check=True)
    r = subprocess.run([sys.executable, "/tmp/scan/decexp.py"], cwd=d, capture_output=True, text=True)
    print(r.stdout.strip())
finally:
    shutil.rmtree(d)
# 2. the PG predicate on a TEMP table
PAT = r'"+-?[0-9]+(\.[0-9]+)?[eE][+-]?[0-9]+"+'
sql = f"""
create temp table dctl (id int, body jsonb);
insert into dctl values (1, '{{"lower": "1E-7"}}'), (2, '{{"lower": "0.0000001"}}'), (3, '{{"exposure_years": "1.2E-28", "u": "10"}}');
select count(*) from dctl r where r::text ~ '{PAT}';
"""
r = subprocess.run(["docker", "exec", "gi-pricing-postgres-1", "psql", "-U", "gipricing", "-d", "postgres", "-At", "-c", sql], capture_output=True, text=True)
print("PG predicate on TEMP table (2 planted exponent rows of 3):", r.stdout.strip().split("\n")[-1])
```

**5. Stored values (not asked for by the maintainer's count; measured for the severity).** The maintainer asked for committed artifacts only; a
read-only scan of the reachable PostgreSQL databases gives the stored side. *Predicate* (`decexp_pg.py`): per
table, `select count(*) … where r::text ~ '"+-?[0-9]+(\.[0-9]+)?[eE][+-]?[0-9]+"+'`, i.e. a quoted exponent-form
decimal, with one or two quote characters because a `jsonb` column renders its quotes doubled inside a record's text
(the lesson of FD 9949's positive control, working id 9949), in `BEGIN TRANSACTION READ ONLY` with `PGOPTIONS='-c
default_transaction_read_only=on'`. *Corpus:* **81 databases, 3841 tables**. *Result:* **0 rows**. *Positive
control:* a `TEMP` table with `{"lower": "1E-7"}`, `{"lower": "0.0000001"}` and `{"exposure_years": "1.2E-28", "u":
"10"}`: the predicate counts **2** (the two exponent rows; the plain one is not counted). *Population for the hashed
fields:* `decpop_pg.py` counts `regression_suite_versions` in the **15** databases that have the table: **0** suite
versions in all of them, so no stored suite (and no stored `lower` or `upper`) exists to hash. Both multi-database runs
took a gate slot (`gate-1`, `uptime` `15:38:08` load 6.35 to `16:02:08` load 7.69; `gate-2`, `16:09:38` load 4.77 to
`16:09:49` load 5.05). **Not measured:** MinIO objects (a JSON artifact written to the blob store), and any environment
beyond this box; the predicate for it is the same string match over each JSON object's string values. The committed
count (evidence 4) and this stored count are both 0.

## Severity

The maintainer's routing, in `~/gi-pricing-plan.local/channel/to-lead.md`, "2026-09-30 16:34:36 BST — RL 9963 fix
(9b15183cdf8ccca3e6fd1129c4ea1b0c72601cd7): decisions on condition 2, the line's scope, and DecimalStr" (outside the
repository; item (3) quoted verbatim):

> **(3) DecimalStr exponent serialisation: file the FD now, not the backlog.** It sits in content-hashed artifacts, so the longer it goes unfixed the more stored hashes a fix would move. The FD states:
>   - how many committed artifacts contain an exponent-form value today (measured);
>   - the fix direction: positional form, with a hash-migration or version-bump note;
>   - an owner (WK-1178 unless model-schema ownership says otherwise).
>   I set severity after the count.


The maintainer's ruling, in `~/gi-pricing-plan.local/channel/to-lead.md`, "2026-09-30 17:15:31 BST — RL 9963 delta
noted; FD 9968 (#1004 at e084655f69d50b988fa263cf9af7d0fcf8ad4a41) severity MEDIUM" (quoted verbatim):

> - **FD 9968: MEDIUM**, over LOW. Two properties justify it, not the count:
>   1. DecimalStr's serialiser emits strings its **own published JSON Schema pattern rejects** ("1E-7", "1.2E-28", "1E+2"): the contract contradicts itself, across 13 fields in 8 models;
>   2. a governed hash (`suite_content_hash`, regression.py:219, unversioned) depends on spelling, so equal values hash differently. That is a reproducibility defect in the audit trail, the property the platform promises (CLAUDE.md §1).
>   **The zero count sets the fix, not the severity:** with 0 committed and 0 stored instances, fix it NOW without a hash-version bump. **The fix commit re-measures the count** (tracked blobs, the PostgreSQL DBs, **and MinIO**, which the FD did not measure) and records 0 as the reason no migration is needed. If any instance appears at fix time, it bumps the `suite_content_hash` version.
>   - Owner **WK-1178** (§1.9 hotfix routing; WK-657 and WK-692 are closed), accepted. The fix follows spec and contract first: DecimalStr's serialisation is a model-schema contract change, so regenerate with contract-guard green.

**Corrected by** the entry "2026-09-30 17:20:19 BST — CORRECTION to my FD 9968 severity entry: "13 fields in 8 models" → "13
fields in **11** models"": the 13 fields are in **11 distinct models** (`DoubleLiftBin`, `VersionTotals`, `AeCell`,
`LiftBin`, `BandingMinimums`, `LargeLossTreatment` (two fields), `Reconciliation`, `Histogram`, `LevelCount`, `OneWayRow`,
`MonotoneInInput` (two fields)), as evidence 2 lists them. The entry says the severity (medium) and both reasons are
unchanged ("The reach is wider, not narrower"), and adds: "**Add to the fix commit's re-measure:** audit-event writers
were spot-checked, not swept. The fix sweeps every DecimalStr write path it touches, or states which paths it measured."
This record's earlier proposal was medium too, for the same two properties plus the count; the maintainer's reasons
above replace it, and the eight-model figure it used is withdrawn.

## Disposition

**Proposed by the auditor; the verdict is the lead's.** The maintainer's decisions (the 17:15:31 and 17:20:19 BST entries, quoted
under *Severity*) are recorded below.

- **Fix direction.** Serialise positionally, as RL 9963 already rules for the ladder's own decimals
  (`PositionalDecimalStr`: the same float refusal and the same JSON Schema, and a serialiser that renders
  `format(value, "f")`). Two decisions belong to the fix's plan, not to this finding: (a) **whether `DecimalStr` itself
  changes or a second type is kept** (RL 9963 kept `DecimalStr`, to avoid changing stored bytes in S3; this finding
  is the count that decides it), and (b) **whether to also normalise trailing zeros** so equal values have one
  spelling (`66000.440` and `66000.44`), which the positional form alone does not do. Normalising and rendering
  positionally together makes the serialised form a function of the value.
- **Hash handling: fix now, with no version bump, unless the re-measure finds an instance (the maintainer's decision).**
  `suite_content_hash` has no version today; `spec_hash` does (`SPEC_HASH_VERSION`, `v11:` prefix and the same number
  inside the payload; the precedent is that a digest of an older version is "stale and findable with `LIKE 'v10:%'`").
  Because 0 committed and 0 stored instances were measured (evidence 4 and 5), the fix goes in **now without a hash-version
  bump**. **The fix commit re-measures the count** over the tracked blobs, the PostgreSQL databases **and MinIO** (which
  this record did not measure), and **records 0 as the reason no migration is needed**. If any instance appears at fix
  time, that commit bumps the `suite_content_hash` version (the `spec_hash` precedent) instead.
- **A `model-schema` contract change: contract first.** `DecimalStr`'s serialisation is a contract change, so the
  contract is regenerated (`docs/contracts/`, the generator's `--check` green) and the contract guard
  (`backend/tests/test_contracts.py`, the `contract-guard` skill) is green before the code lands; the spec comes first
  (`CLAUDE.md` §0).
- **The write-path sweep (the 17:20:19 BST entry).** The fix commit **sweeps every `DecimalStr` write path it touches, or
  states which paths it measured**: the serialiser is reached wherever a model holding one of the 13 fields is dumped
  (the persisted `jsonb` rows, blob payloads, API responses, the `suite_content_hash` payload), and audit-event writers
  were spot-checked, not swept. This finding measured the tracked blobs and the PostgreSQL databases (evidence 4 and 5)
  and did not sweep the individual writers; that sweep is the fix commit's.
- **Owner: WK-1178**, the standing maintenance Work (`docs/roadmap.md`, the WK-1178 row: "work that belongs to no other
  Work"; `docs/process/document-ids.md` §1.9 routes hotfixes there). No Work in the roadmap owns `model-schema` as a
  component: the rows that name it are `WK-657` (repo foundations, closed) and `WK-692` (Phase 1b's non-browser
  work, closed), and `document-ids.md` names `model-schema` only as the source the contracts are generated from
  (`:171`). A `model-schema` type change also regenerates `docs/contracts/` and runs the contract guard
  (`backend/tests/test_contracts.py`, the `contract-guard` skill), which the slice's write set must carry.
- **Acceptance, red first:** `Decimal("0.0000001")`, `Decimal("0.00000000000000000000000000012")` and
  `Decimal(100).normalize()` each serialise to a string that matches the type's JSON Schema pattern; two value-equal
  inputs (`"10"` and `"1E+1"`; `"66000.440"` and `"66000.44"`, if normalising is chosen) give one serialised form and one
  `suite_content_hash`; a generated-contract validation of a model dump for a small value passes.

**Event that next confirms or discharges it:** the WK-1178 slice merges with a positional (and, if decided, normalised)
serialiser, the contract regenerated, and the `suite_content_hash` handling (a recorded zero count from the re-measure over tracked blobs, PostgreSQL and MinIO,
or a version bump if an instance appears) and the write-path sweep.

## Decision

Not yet decided. The proposal above is the auditor's; the lead adopts, amends or rejects it. The severity and owner
are the maintainer's.

Ownership shape: event
