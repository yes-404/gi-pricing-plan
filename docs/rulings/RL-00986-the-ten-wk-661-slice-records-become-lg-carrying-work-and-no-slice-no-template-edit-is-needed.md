---
id: RL-986
family: ruling
title: the ten WK-661 slice records become `LG-`, carrying `work:` and no `slice:`; no template edit is needed
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-guard-arithmetic-and-ledger-family-rulings.md
---

## RL-986 — the ten WK-661 slice records become `LG-`, carrying `work:` and no `slice:`; no template edit is needed

### 1. Verified first, at `ffac8ba`

**(a) What the ten are.** Rows 12–21 of the derivation's 21-row enumeration, all in
`docs/closures/INDEX.md#closure-recordsmd`, all headed `WK-661 — <slice>, 2026-08-1{5,6,7} *(in progress, not
closed)*`. The derivation establishes they are per-slice delivery records, quoting row 12's own
closing paragraph: *"**WK-661 is not closed and this is not a closure record.** It is one slice of …
requirements, written down so the next one starts from what is true."* The *"in progress, not
closed"* qualifier describes **WK-661's state when each record was written**, not the slice's: row
5 of the same file is `WK-661 — Modelling: closed 2026-08-22`, and `docs/roadmap.md:232` carries
`| **WK-661** | Modelling workbench … | ✔ **closed 2026-08-22** |`.

**(b) `_discover_closure_records` raises on them today**, which is the correct behaviour and
the reason this is a decision rather than a code change (`scripts/doc-id.py:1240-1245`):

```python
if "not closed" in trailer.lower():
    raise NotImplementedError(
        f"migrate: {path}, heading {title!r} ({date_str}) is not yet closed -- "
        f"migrate cannot assign a family a governed document does not have (task "
        f"#31). Resolve the record's disposition (or close it) before migrating."
    )
```

**(c) The derivation's sole ground for rejecting `LG-` is false, and I re-measured it rather
than taking the refutation's word.** §3.2 argued that `docs/_templates/LG.md` declares
`slice: SL-NNNNN` unconditionally, making it **required** under RL-981, with no `SL-` row
in existence to name. Executing `derive_field_policies()` against the real templates:

```
ledger permitted: corrected_by created family id owner phase plans relates
                  slice status title tree work
ledger required : created family id owner status title
  'slice': permitted=True  REQUIRED=False
  'work' : permitted=True  REQUIRED=False
```

RL-981 governs the **permitted** set. Required-ness is a separate mechanism —
`required = frozenset(_CORE_HEADER_FIELDS) & permitted`, plus `{"id"}` — and `slice:` is not a
core field. **A ledger with no `slice:` passes check 30.**

**(d) A second, independent ground the refutation did not use: the template says so itself.**
`docs/_templates/LG.md`'s own comment block instructs *"delete this comment block, and **remove
any field this ledger does not use**."* Omitting `slice:` is not a tolerated gap; it is the
documented way to use the template.

**(e) The §1.7 residual — the derivation's stated reason for not taking its own
recommendation — corrected, and then answered.** The refutation wrote that §1.7 *"routes the
terminal row through either axis — 'a `CR-` cites the plan's `slice:`/`work:`'"*. **That
quotation drops a conjunct.** §1.7's table reads, for the terminal row:

| `closed` | a `CR-` cites the plan's `slice:`/`work:` **and the `SL-` row is `closed`** |

With no `SL-` row, that row cannot be reached. The refutation's conclusion survives, but not
by the route it gave, so the real answer is recorded here:

- **`execution` is a property of a `PL-`, never of an `LG-`.** §1.7: *"`doc-index.py` derives it
  into an `execution` column"* for a plan. A ledger has no execution column to lose.
- **No `PL-` routes through any of the ten.** The earliest filed plan is
  `docs/plans/PL-00731-the-profile-contract-histogram-rename-and-the-generated-counterpart.md`; the ten are dated 2026-08-15 to 2026-08-17 and
  predate the convention. `grep -rl` across `docs/plans/` for their headings returns only the
  derivation itself. Their `plans:` is empty, so no plan's column is computed through them.
- The 16 existing `-ledger.md` files are in the identical position and carry no front matter at
  all today.

**(f) `work:` resolves, and the "no slice rows" claim is tested against both decorations.**
`docs/roadmap.md` carries 56 leading work rows over 41 distinct ids (§1(g)), three of them
`WK-661`'s. Per-slice rows are **zero under every decoration** — `^\|\s*\*\*W<n>-<m>\*\*`,
`^\|\s*~~\*\*W<n>-<m>\*\*~~` and the union all return 0 — which matters because §1(g) shows a
`\*\*W`-anchored count missing 26 rows, and a "zero" from a blind pattern would be worthless.
Twenty-three `W<n>-<m>` tokens do appear in the file, as prose and cell text rather than as row
heads. W37-6 converts works to `WK-` rows in the same commit that creates
these ledgers, so `work:` names a row that exists post-migration. `slice:` would name nothing,
which is the reason to omit it rather than a reason to invent a row.

### 2. Ruled

**All ten become `LG-`, `family: ledger`, in `docs/ledgers/`, carrying `work:` set to WK-661's
post-migration `WK-` id and **no** `slice:` field. `docs/_templates/LG.md` is not edited.**

This is the derivation's recommendation (e) **minus its template edit**, which §1(c) and §1(d)
show to be unnecessary. Recording the difference matters: (e) proposed *"`slice:` made
conditional in `docs/_templates/LG.md`"*, and adopting it as written would edit a template to
license something the template already licenses — a change to §1's surface for no gain, which
RL-981 held goes back to the maintainer.

- **`status:`** is `LG`'s own vocabulary, `active → closed`, and §1.6 gives it to the auditor
  *"at slice close"*. WK-661 closed 2026-08-22, so the expected value is `closed` — but each of the
  ten is read for its own outcome rather than blanket-stamped, and any that records a slice
  that did not complete takes `retired` with the reason in its body. **Ten reads, not one
  assumption.**
- **`owner:`** is `executor`, per §1.6's `LG` row and the template's own default.
- **`created:`** is each record's own date, per RFC-937 §4 step 1.
- **`phase:`** is WK-661's phase, derived at migration time.

**Rejected: (a), `LG-` with `SL-` rows minted retroactively.** The derivation rejected it and
the refutation independently closed it: *"Minting `SL-` rows out of the map plan's slice table
would be creating governed rows rather than converting them — outside §4's 'one scripted PR,
once' over existing things."* §1.6 also makes `SL` the planner's, cut in a map plan; WK-661 had none.

**Rejected: (b) `RS-`.** Wrong unit — these are delivery records, and row 12 distinguishes
itself from the audit shape in its own text.

**Rejected: (c) `CR-`.** RL-975 already, and independently §1.2: `CR`'s status subset is the
single value `active` and its unit is *"one work, phase or review close"*. These are not closes.

**Rejected: (d) consolidation into one document.** Destroys the per-slice unit that is the only
record of ten slices, and matches no §5.2 rule.

**Rejected: leaving them `UNDETERMINED` until the run.** This is what the maintainer's
instruction forecloses, and §1(b) shows the cost — `migrate` raises on the first of the ten, so
the run stops at a decision nobody is positioned to take on the day.

### 3. What it obliges

1. **`_discover_closure_records`'s `"not closed"` branch stops raising and emits an `LG-`
   draft** with the fields of §2. The raise was correct while the family was undecided and is
   wrong the moment it is decided; it is replaced, not deleted, by the classification.
2. **The ten join the 16 existing `-ledger.md` files in `docs/ledgers/`**, which §5.2 already
   routes there. `docs/ledgers/` does not exist at `ffac8ba` and is created by the migration.
3. **No `SL-` row is minted for any of them**, and their absence is not a defect to fix in the
   standard: §4 step 3 converts slices that exist in the roadmap and there are none in any
   shape, so the clause is vacuous rather than unsatisfiable.
4. **Rows 12–21 of the derivation's §1 table move from `UNDETERMINED` to this ruling.** The
   derivation is frozen at its date and is not edited; this record is its resolver, and the
   derivation's Acceptance Standard item 4 — which makes materialising them early a detectable
   violation — is discharged by that resolution rather than by an edit.
5. **`slice:` stays permitted for every other ledger.** Nothing here narrows the field; a
   ledger cut from a map plan carries it as the template shows.
6. **RL-985's census lands with this or before it, never after.** RL-985 §1(b) shows the
   guard at `:1829-1831` is unreachable for `closure-records.md` today, because the raise this
   ruling removes pre-empts it. Removing the raise on its own therefore does not restore a
   working guard — it exposes one whose blind spot has simply been hidden. The two changes are
   ordered, and this is the ordering.

### 4. Acceptance — the violation that must become detectable

**The violation: one of the ten materialises as anything other than an `LG-` in
`docs/ledgers/`, or carries a `slice:` naming a row that does not exist.**

- **A test that runs `_discover_closure_records` against the real
  `docs/closures/INDEX.md#closure-recordsmd` and asserts 21 drafts: 8 `CR- kind: work`, 1 `CR- kind:
  phase`, 2 `RS- kind: audit`, 10 `LG-`.** *Violation: any count other than 21, or any of the
  ten emitted under another prefix.* It must fail today with the `NotImplementedError` of
  §1(b) — the positive control the corpus already supplies.
- **A check that no emitted `LG-` carries a `slice:` whose value resolves to no roadmap row.**
  *Violation: a `slice:` naming nothing.* This is the clause that would have caught the
  derivation's original concern had it been real, and it must red on a deliberately broken
  fixture carrying `slice: SL-99999`.
- **A check that every emitted `LG-` carries a `work:` that does resolve**, once W37-6 has
  created the `WK-` rows. *Violation: a ledger with neither axis.* This is the substantive
  content of §1(e) — the ten are permitted to omit `slice:` because `work:` is present, not
  because both may be absent.
- **`status:` is read per record.** A fixture in which one of the ten states a slice that did
  not complete must produce `retired`, not `closed`. *Violation: ten records taking one status
  from one reading.*

---

## Where the wrong `plan-reviews.md` figures came from — a merged commit body, which cannot be corrected in place

**Not a ruling, filed here because it explains why a wrong figure survived three careful
readers and because the artifact carrying it cannot be edited.**

The lead routed RL-978's question with *"15 `###` headings, 12 records, three
undated … read as sub-content nested inside 'Plan review 9''s own section"*, corrected it on
its own initiative after the maintainer challenged it, and named an executor's report as the
source. The report was not the origin. `#585`'s **squash commit body on `main`** (`20b3025`)
reads:

> Fifteen `###` headings produce twelve records, and three of the fifteen carry no date at
> all, reading as sub-content nested inside another review's section rather than as
> independent records. No regex reaches that: the per-heading model may simply be the wrong
> shape for that file. Filed, not fixed.

Measured at `ffac8ba`: **14 headings, 10 records, four unaccounted** — the fourth being a filed
plan review, which the sentence above cannot describe because it counts only undated ones. The
figures reached the lead's brief through a chain in which nobody was careless: each reader was
citing a merged commit on `main`.

**Two things follow, and only the second is actionable.** First, `main`'s history is immutable
under the `main-protection` ruleset — squash bodies cannot be rewritten — so the wrong sentence
stays where it is and a reader who finds it has no in-place correction to find. Second, the
correction therefore has to live in a document that the commit's subject can be traced to.
[RL-978](RL-00978-the-three-undated-headings-are-sub-content-of-one-dated-container-section-no-widening-and-the-container-s-family-is-the-planner-s-to-derive.md) carries the measured figures and their probes; this paragraph names where
the superseded ones came from, so a reader arriving from `git log` has somewhere to land.

The general point, which is why it is filed rather than mentioned: **a figure in a commit
message is a citation target with no correction mechanism.** A count that a later reader will
act on belongs in a document that can be amended, and the commit body should point at it.

## Not ruled — and where each goes

| Item | Why not mine | Where it goes |
|---|---|---|
| **What `RL-902`, `A2` and `A3` are** (`2026-08-30-nt-0012-0013-0014-adoption.md:67,81,96`) | Surfaced by RL-985's measurement, but deciding whether a letter-suffixed id is a ruling, sub-content, or a legacy form to renumber is a family and id-form question under RFC-937 §1.2 and §1.7 — the same species the planner derived for the twelve. I have not enumerated the option set | **The planner**, as a derivation, then back here. It is a RL-985 precondition: the census cannot be cleared while three units are unclassified |
| **The three h1 ruling files** (`RL-949`, `60`, `61`) | A fact, not a decision — one ruling per file, so the multi-ruling splitter should not be reading them at all. Whether it currently tries is a code question | **W37-6's executor**, as a measurement during the census. If the splitter does try to split them, it is a new finding |
| **Whether `_discover_register`'s row unit needs the same treatment** | RL-985's property is worded to cover it, but the register's shape was not measured here and I will not assert a blind spot I have not seen | **W37-6's executor**, inside the census |
| **The commit boundary for RL-985's fix** | RL-977 settles the principle for this class; §2 applies it and names the one respect in which this fix differs. Merge order itself is the lead's | **The lead** |
| **Whether the ten WK-661 slices each completed** | Evidence, not a decision. §2 fixes the rule; reading ten records against it is execution | **W37-6's executor**, per RL-986 §4's fourth item |

## Provenance

Routed by the lead on 2026-09-02, both as maintainer requests. RL-985's property is the
maintainer's own words and its design is ruled here; RL-986 adopts a planner recommendation
one step smaller than as written, on two grounds the derivation did not have.

The lead's routing message corrected its own earlier `plan-reviews.md` figures unprompted, and
the corrected figures agree with the independent measurement filed as Rulings 81-82. Chasing where
the superseded ones came from produced the finding two sections above: they are quoted from a
merged commit body on `main`, which is why three readers passed them along unchanged. **No
figure in this record is taken from a relay** — every one was produced by executing the script
or reading the shipped source at `ffac8ba`, including the ones that turned out to agree with
what was relayed.
