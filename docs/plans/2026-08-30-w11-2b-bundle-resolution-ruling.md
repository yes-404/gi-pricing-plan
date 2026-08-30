# W11 Task 2B — resolving a rating-version ref to its compiled `Bundle` (2026-08-30)

**What this is.** The ruling on the Task 2B blocker raised by `w11-executor-s2a`: the plan's
step 4 says *"Resolve the ref to its `Bundle` — metadata read, then the blob store"*, and
neither half exists. **Critical path — Task 2B cannot finish without it.**

**Numbering continues at 37.** Rulings 1–30 are catalogued in
[`2026-08-29-w11-3-d6-batch-resumability-ruling.md`](2026-08-29-w11-3-d6-batch-resumability-ruling.md);
31–32 there, 33 in
[`2026-08-29-w11-slice-parallelism-ruling.md`](2026-08-29-w11-slice-parallelism-ruling.md),
34 in
[`2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md`](2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md),
35 in
[`2026-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md`](2026-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md),
36 in
[`2026-08-30-w11-nfr-rate-11-quote-input-stores-ruling.md`](2026-08-30-w11-nfr-rate-11-quote-input-stores-ruling.md).

**Mints no `FR-`/`NFR-`/`OQ-` id, and makes no edit in this commit.** §5 explains why the spec
change this ruling authorises lands **with** the code rather than ahead of it: this is
`CLAUDE.md` §0's **first** row, not its second.

**Read against `origin/main` at `7952f76`**, the same tree the blocker was raised at.

---

## Ruling 37 — option (c): the compiled bundle's blob key becomes part of the version's own metadata

**Ruled: (c).** `BundleMetadata` gains a nullable blob-key field, written by the `rating.compile`
handler in the transaction that already writes the row, and read by the scoring route. **(a) and
(b) are refused, and (a) on a stronger ground than cost.**

### 1. Every premise checked, and one is overstated

Each read at `7952f76` rather than taken from the report:

| Claim | Verdict |
|---|---|
| **(a)** no ref→row resolver | **Confirmed.** `rating_versions.py` exposes `to_schema`, `load_rating_version`, `create_rating_version`, `submit_for_review`, `apply_approval_decision`, `compile_rating_version` — nothing keyed on an `ArtifactRef` |
| **(b)** no row→blob linkage | **Confirmed.** `BundleMetadata` declares exactly `content_hash`, `bytes`, `compiled_at` under `extra="forbid"` |
| **(c)** `content_hash` is not the blob key | **Confirmed as a fact, overstated as a hazard** — see below |
| **(d)** the key lives only in a Job row | **Confirmed.** `rating_handlers.py` returns `JobResult(kind="blob", ref=ref.sha256)`, and `JobRow.result` is un-indexed JSONB |
| no migration needed | **Confirmed.** `db/models.py:1910` declares `bundle` as a nullable `JSONB` column via `mapped_column(JSONB)` |

**The overstatement, corrected because it points the other way.** The report says code confusing
the two hashes *"would typecheck, pass a `BlobRef` pattern check, and fail at read time."* It
would not. `BundleMetadata.content_hash` is `^sha256:[a-f0-9]{64}$` and `BlobRef.sha256` is
`^[a-f0-9]{64}$` — **the prefix differs, so a naive pass fails Pydantic validation loudly at the
boundary.** The silent path exists only for code that strips the prefix first. The hazard is
real but narrower, and the correction is load-bearing for §3: it means the *pattern difference
is already a working guard*, and the new field should be specified so as to keep it.

### 2. Why (a) is refused — and not because it is slow

The report prices (a) as an un-indexed JSONB scan on a 50 ms budget. That is true and would be
enough. **The disqualifying objection is elsewhere:** (a) requires choosing *"the latest
succeeded `rating.compile` job"*, and a recompiled version has several such rows.

**That is a decision about which compiled artifact a rating version *is*, and it would be made
inside a query.** A rating version is the authority for its own identity; making Job history the
authority inverts the model, and the choice would never appear in a requirement, a ruling or a
review — it would be a `ORDER BY finished_at DESC LIMIT 1` that nobody had to defend. `CLAUDE.md`
§0 exists to stop exactly that.

It is also a **durability** defect, not only a performance one. Job rows are operational records
with their own retention and pruning concerns; a rating version whose only link to its compiled
bundle lives in Job history becomes unresolvable the day that history is trimmed. The linkage
between an artifact and its compiled form belongs in the artifact's own metadata.

### 3. Why (c), and how the field is specified

**(b) is refused on the requirement.** FR-RATE-24 has the bundle *"compiled once, distributed,
and cached"*; recompiling per miss inside the request contradicts it and cannot meet NFR-RATE-1.

**(c) is cheap because the plumbing already exists.** `_rating_compile` calls
`compile_rating_version(session, …, blob_store=…)` and then `blob_store.put(session, …)` **in
the same `unit_of_work`**. The row write and the blob key are already inside one transaction, so
carrying the key into the row adds no I/O, no round trip and no new dependency. `row.bundle` is
JSONB, so no Alembic migration.

**The field, specified so the §1 confusion cannot be written down:**

- **Name it for what it is — a blob key, not a hash.** `blob_sha256`, never `hash`-suffixed.
- **Pattern `^[a-f0-9]{64}$`, bare hex**, matching `BlobRef.sha256` and *not* `content_hash`'s
  prefixed form. **A `content_hash` value then cannot validate into this field and a
  `blob_sha256` cannot validate into `content_hash`** — the schema refuses the mix-up rather
  than documenting it. This is the point §1's correction earns.
- **Nullable in the contract**, for the reason in the block below — which is not the reason it
  first appears to be. No migration, no back-fill job, no historical scan.

**What a version compiled before the field existed resolves to.** Raised by the executor and
settled here rather than in W14. **It resolves to nothing, and the route refuses** — but the
ruling defines the reader's behaviour instead of relying on the population being empty, and the
three halves are separated because they have different answers:

- **Contract: nullable — and the reason is `to_schema`, not tolerance for legacy rows.**
  `rating_versions.py:83` does `BundleMetadata.model_validate(row.bundle) if row.bundle else
  None` on **every read of a rating version**. A required field would turn a single keyless row
  into a hard validation failure of *every* read of that version — the list route, the get
  route, the approval paths — not merely a failed scoring attempt. **Nullable keeps the blast
  radius at the thing that actually needs the key.**
- **Writer: mandatory.** `row.bundle` has exactly one writer — `rating_versions.py:379`, the
  compile path; `git grep` over `backend/src` and `packages` finds no other assignment, no demo
  seed and no data migration that writes it. So the invariant *"a compiled bundle carries its
  key"* is enforceable at a single source, and should carry a test asserting it rather than
  being left to hold by construction.
- **Reader: refuse, and distinguishably.** The scoring route refuses, with an error naming
  **this** condition — compiled but unresolvable — and **not** the one it uses for a version
  that was never compiled. The operator's remedy is the same (recompile); the diagnosis is not.
  Never-compiled is an ordinary workflow state; a keyless-but-compiled row is a **data defect**,
  and collapsing the two hides it in exactly the environment where someone would need to see it.

**Why this is better than "nothing, and the route refuses" on its own.** That answer is cheap
because no such row exists today, and it stops being cheap the moment one does — the objection
the escalation itself raises. Defining the reader's behaviour removes the dependency: **the
ruling never expires, because it does not rest on the population staying empty.** The emptiness
is confirmed (single writer, no seeds, no data migration) and is used only to establish that no
back-fill is owed — not to license leaving the case undefined.
- **`bytes` is not duplicated.** `BundleMetadata.bytes` is already the serialised length, which
  is the blob's size, so only the key is missing.

**One ordering detail the executor would otherwise find at the keyboard:**
`compile_rating_version` writes `row.bundle` *before* the handler performs the `put`, so the key
does not exist at the moment the row is written. Either move the `put` inside
`compile_rating_version` — which already receives `blob_store` — or update the row after the
`put` within the same `unit_of_work`. Both are correct; the first keeps the row write and its
key in one place. **Not mandated.**

### 4. What this does not decide

Whether a rating version should retain *several* compiled bundles (one per recompile) rather
than one current key. This ruling gives it one, because that is what step 4 and FR-RATE-24's
"compiled once" describe, and because nothing in W11 needs more. **If a later workstream needs
history, that is an additive change to the same field, not a reversal of this ruling** — and it
would then need the "which one is live" policy that §2 refuses to have invented silently.

### 5. Disposition — the spec change lands with the code, not ahead of it

Three artifacts declare this shape, and **all three must change together**:

1. `packages/model-schema/src/model_schema/rating.py` — `BundleMetadata` (**the source of
   truth**, ADR-0002).
2. `docs/specs/03-rating-engine.md:359` — the §4.3 artifact example, currently
   `"bundle": {"content_hash": …, "bytes": …, "compiled_at": …}`.
3. `docs/contracts/schemas/rating-version.schema.json:26-34` — the **hand-authored** contract
   tier (it is not under `schemas/generated/`), whose `required` list names the same three keys.

**This role makes none of the three edits in this commit, and the routing is `CLAUDE.md` §0's
first row rather than its second.** The blocker report reads it as row 2 — *"a capability not
yet specified"*, hence *"spec change first"*. **It is not.** The capability is specified twice
over: FR-RATE-34 (`03`:161) has scoring *"evaluate one Quote Context against the Rating Version
currently live"*, and FR-RATE-24 (`03`:135) has that version compile to a Bundle that *"is what
gets cached and distributed"*. Resolving a live version to its compiled bundle is not a new
capability — it is the one those two already require. What is missing is a field in the data
contract that the specified behaviour needs, which is exactly row 1's *"**Code**, plus any spec
change it proves necessary"*.

So the edits land **together, in the executor's commit**, which is also where the regenerated
contract and `generate-contracts.py --check` belong. `CLAUDE.md` §2 requires that anyway for a
change spanning spec and code, and here the two rules agree: splitting them would open a window
in which a spec declares a field the contract and code lack, and **F27 records that nothing in
the gate compares a spec's declared shape against its hand-authored contract**, so that window
would not be caught.

**Why the mis-routing is worth naming rather than quietly fixing.** Row 2 would have sent a
blocked task through a spec cycle before a line could be written, on the critical path. The
distinction that decides it is *capability* versus *contract*: a field the specified behaviour
already requires is row 1, however much schema it touches. Reading a schema change as
automatically row 2 is what produced the delay here.

**Unblocked immediately, per the report's own division:** Task 2B steps 3 and 4's 409 refusal
branch and its discriminating test, and step 6's RBAC cases, sit before resolution and were
never blocked.

**The ruling is overridden** if the blob key is written anywhere that is not the rating
version's own metadata, if a "latest succeeded job" query appears on the scoring path, or if
the new field is given `content_hash`'s prefixed pattern — which would re-open the confusion
§3 closes.

---

## Verification

- **Tree:** `7952f76`, `origin/main`, the same commit the blocker cites — checked equal rather
  than assumed, because the report was written against it and the tree has been moving all
  night.
- **Each of the report's four claims was re-read at source**, not accepted: the service
  function list, `BundleMetadata`'s fields and `extra="forbid"`, the handler's `JobResult`, and
  the `JSONB` column. **The one that did not survive is (c)'s hazard**, and it was found by
  reading the two patterns against each other rather than by reading either alone.
- **The three declaring artifacts were enumerated by searching for the shape**, not recalled —
  which is how the hand-authored `rating-version.schema.json` entered the disposition. Confusing
  the hand-authored tier with `schemas/generated/` would have produced a disposition telling an
  executor to regenerate a file that is not generated.
- `python3 scripts/audit-docs.py` — run before commit.
- **Makes no `docs/specs/` or `docs/contracts/` edit**, so it introduces no window in which the
  three declarations disagree. Mints no id and registers no error code, so it owes no
  [`../open-questions.md`](../open-questions.md) mirror row and no
  [`../roadmap.md`](../roadmap.md) §10 gate row.
