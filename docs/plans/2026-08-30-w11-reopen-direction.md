# W11 reopen — the maintainer's direction, recorded (2026-08-30)

**What this is.** The maintainer's instruction to reopen the uncompleted part of W11, quoted
verbatim and dated. It exists because Ruling 39 clause 1 made it a precondition: until the
direction is in an artifact, the reopen rests on the lead's relay, and the W11 closure record
would be annotated on authority no later reader could find.

**Raised by the decision-maker, not by the lead.** The dispatch that requested Rulings 39–41
asserted the direction as established fact. The decision-maker checked the tree, found nothing
carrying it, and declined to build the ruling's shape on the relay — `CLAUDE.md` §12: *"Every
decision lands as a dated artifact — a ruling record, an audit record, a plan — never in
chat."* This record is the correction.

## 1. The direction

Received 2026-08-30, in the maintainer's own message opening this session, verbatim and
complete:

> *"read handover in /home/puzhenhao1989/gi-pricing-plan.local, spawn the team; landing
> NT0012, 13 and 14; reopen the uncompleted W11, follow the process to the end of W11"*

Nothing else in that message bears on W11's scope, and no later maintainer message in this
session has amended it.

## 2. What it does and does not authorise

**It reopens W11.** The reduced-scope close of 2026-08-30 (`docs/audit/work/W11/README.md`)
recorded three requirements as *not started*; *"reopen the uncompleted W11"* directs that they
be built. Ruling 39 fixes the scope at **FR-RATE-36, FR-RATE-37 and FR-RATE-42**, and with
FR-RATE-42 the NFR-RATE-12 that the closure record §6 tied to it.

**It does not authorise the lead to accept the re-close.** This is the point on which the
earlier delegation must not be stretched. The maintainer's 2026-08-30 delegation —
*"plz mind that I have already authorised you to decide W11 close"* — was given for the close
that then happened, and both `docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md` §1.1 and the
closure record read it narrowly. A delegation to decide *one* close is not a standing licence
to decide the next one. **The re-close returns to `CLAUDE.md` §12's default: acceptance of a
Work close is the maintainer's, with a dated line.**

**It does not fold the adoption into W11.** *"landing NT0012, 13 and 14"* is a separate
instruction in the same message, and the adoption is a separate Work with its own filed record
and its own bounded delegation (Ruling 39 §1). Slices E, F and G continue under
`2026-08-30-nt-0012-0013-0014-adoption.md`.

## 3. One thing this record deliberately does not settle

**Whether NFR-RATE-1's remediation belongs inside the reopen.** NFR-RATE-1 was not
*uncompleted* at the close — it was measured, and it failed, and it was carried forward with a
named resolution. So the plain reading of *"the uncompleted W11"* does not reach it, and Ruling
39 scoped the reopen without it.

What has changed since is that **Ruling 41 makes the dominant term cheaply removable**: the
version-row read stays on the hot path while the blob lookup, the ~2 MB object read and the
full `model_validate_json` leave it, with **zero staleness window**. That was not known when
the close was written.

This is a scope question for the maintainer, not one the lead may settle by widening the work
it was given. It is **raised**, not assumed, and the point is recorded here so that a later
reader can tell a deliberate exclusion from an oversight. **Note that removing that term does
not make NFR-RATE-1 pass**: the 15 ms without-GBM limb already reads component p99 23.027 ms
with the fetch excluded, and Ruling 41 declines to amend the requirement or to call it
reachable.
