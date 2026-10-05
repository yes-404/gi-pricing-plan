---
id: FD-1414
family: finding
title: A validation run and a model approval never check Rule Set member status; FR-50's run-time clause is enforced only at replace_rule_set
status: active
created: 2026-10-05            # the mint date (check 31); filed 2026-10-01
owner: auditor
tree: 49cd25be441382aebc1cc9c9ff325bd73fd81bc1
corrected_by: []
relates: [WK-1178, FD-1356, FR-50, FR-45, FR-48, FR-51]
---

# FD-1414 — A validation run and a model approval never check Rule Set member status (FR-50)

## Finding

**Corrected 2026-10-01, on the maintainer's entry headed *"2026-10-01 11:10:39 BST — CORRECTION:
option (ii) WITHDRAWN; FD 9748's remedy comes INTO the FD-1356 fix slice (option i); my rationale
conflated two populations"*: the remedy (run-time member-status enforcement plus the silent
missing-member drop) rides IN the FD-1356 fix slice (PL 9762); `dm-1356` rules where, in RL 9750;
the discharge is that slice's merge. The deadline and the "its own FD" disposition below are
superseded; severity stays MEDIUM.** The reason: DP-6 resets `gipricing`'s 10 rows
(~~`user_approved_no_approved_request=10`, the maintainer's figure~~; count re-attributed to its measurement on the maintainer's instruction, 2026-10-01: the count is the DP-0 re-run by auditor-dp0, PL 9762's Task 0 script run 2026-10-01 10:41:08–10:41:19 BST, output line `gipricing route_approved=0 self_approved=0 user_approved_no_approved_request=10`, column `user_approved_no_approved_request`, recorded in PL 9762's "DP-0's decided record" (#1063)), so without run-time enforcement
the record would say `review` while the run says running. The earlier text is kept below and
struck in place, not rewritten.

> **Amended 2026-10-05 before mint:** working ids that have since minted, re-pointed. **`RL 9750` is
> `RL-1407`** (`docs/rulings/RL-01407-…`, §"FD 9748 (working id)", merged as #1070); **`PL 9762` is
> `PL-1408`** (`docs/plans/PL-01408-…`, Acceptance 23–25 and Step 3b, whose remedy is
> `rule_service.rule_set_to_run`; `status: draft` at `origin/main`
> `ef5dc6e7317281ac9d1840fa61861597e3c1b8b1`, activation PR #1112 open). The
> working ids still written in this essay stand as the quotation of what was written then,
> including inside the maintainer's entry headings quoted above. **Code cites re-checked at that
> tree, none moved:** `rule_set_for` `validation_rules.py:450`, `_to_rule_set` `:511`,
> `replace_rule_set` `:549` (refusal `:596-604`), `data_handlers.py:247` and the dry-run set
> `:241-244`, `api/validation.py:395`, `enabled_entries` `model_schema/validation.py:160`,
> `run_validation` `validate.py:2138` (the `:2150-2154` docstring and the `:2162-2165` loop).
> The remedy is not built: the fix is `PL-1408` Step 3b. The finding's substance is unchanged.

**Severity: MEDIUM, owner WK-1178, ~~deadline before the P2 exit demo~~ (superseded, see above).** All three are the
maintainer's, set in the entry headed *"2026-10-01 11:07:12 BST — #1070 audit: observation (1) →
its OWN FD (option ii), MEDIUM, deadline before the P2 exit demo; observation (2) → an FD,
MEDIUM, remedy RIDES in the FD-1356 fix slice; F1–F4 adopted"* (lead's channel, `to-lead.md`),
and its addendum headed *"2026-10-01 11:07:28 BST — Addendum to observation (1): decision
UNCHANGED (option ii); the silent member drop joins the new FD"*. **Working id 9748**, minted at
the records PR. Raised as an observation by the decision-maker `dm-1356` in RL 9750 (#1070,
"Observed, not ruled") and confirmed end to end by auditor-1070.

**FR-50** (`docs/specs/01-data-management.md:112`), to the clause: *"A custom rule is an Artifact
with its own `draft → review → approved` lifecycle; **only `approved` rules may run in a Rule Set
used for a Dataset feeding an `approved` Model.**"* `01` §4.5 step 3 and step 4
(`01:522-523`) say a rule is approved by an Approver and that an `approved` rule is immutable.

**What happens today: the clause is enforced at one point, when the Rule Set is written, and at
none where a rule runs or a model is approved.**

The run path, at `origin/main` `49cd25be`, each link read:

1. `backend/src/app/worker/data_handlers.py:247`: the validation job calls
   `rule_service.rule_set_for(...)`. (`api/validation.py:395` reads the same function for the
   route. `data_handlers.py:241-244` wraps one rule alone for a dry run, whatever its status;
   that is how a `draft` rule gets its dry run and is not the gap.)
2. `backend/src/app/platform/validation_rules.py:450-473`, `rule_set_for`: selects the newest
   `ValidationRuleSetRow` for the dataset. No status read. It returns `_to_rule_set`.
3. `validation_rules.py:511-548`, `_to_rule_set`: `select(ValidationRuleRow).where(workspace_id,
   id.in_(member ids))`, **no status predicate**; builds a `RuleSetEntry(rule=to_schema(...))`
   for every member found.
4. `packages/model-schema/src/model_schema/validation.py:160-161`, `enabled_entries`:
   `e.enabled` only.
5. `packages/pricing-core/src/pricing_core/data/validate.py:2162-2165`, `run_validation`:
   `entries = rule_set.enabled_entries`, then `_run_one(entry, …)` for each. `validate.py` reads
   no `.status` (`git grep -nE "\.status" -- packages/pricing-core/src/pricing_core/data/validate.py`
   prints nothing).
6. `git grep -nE "APPROVED|\"approved\"|'approved'"` over `platform/validation.py` and
   `worker/data_handlers.py` prints nothing.

**The only status gate** is `replace_rule_set` (`validation_rules.py:549-`; the refusal at
`:596-604`, `RULE_NOT_APPROVED` 409, "Every rule in a rule set must be approved"). It runs when a
set is written. A set stores rule ids, not copies (`_to_rule_set`'s docstring), so a rule that is
`approved` when the set is written and not `approved` afterwards is still a member and still runs.

**Model approval reads no Rule Set either.** `git grep -nE "rule_set|validation_rule|RULE_NOT_APPROVED"
-- backend/src/app/platform/modelling.py backend/src/app/platform/approvals.py` finds only
`approvals.py:112`, the author map entry `"validation_rule": "validation_rule.created"`.
`platform/datasets.py:436` copies `validation_rule_set_id` and nothing more. FR-50's clause names
the case exactly: a Dataset Version validated against a set holding a non-`approved` rule, feeding
an `approved` Model, and no step on the way from validation to model approval notices.

**A second gap in the same function: a missing member is dropped silently.** `_to_rule_set`
builds entries `for member in members if member.rule_id in by_id`
(`validation_rules.py:536`). A member whose rule row does not exist
is skipped, so **a run executes fewer rules than the set declares, with no signal**: not an
`error`, not a layer reported as empty, nothing in the report. `replace_rule_set` refuses an
unknown id at write time with `NOT_FOUND` 404 (`:587`), but a row removed or never written
afterwards is not caught. (Raised by the maintainer in the addendum above. FR-48's rule that "an
unrun rule is never a pass" is about a rule that raises or times out, `validate.py:2150-2154`; it
does not reach a rule that is never loaded.)

## Why it matters

1. **FR-50 is a governance requirement, and its run-time clause is a dead letter.** The rule
   reviewed by an Approver is the control; a set that runs a rule nobody approved gates modelling
   on something nobody reviewed, which is the reason the write-time refusal itself states
   (`validation_rules.py:600-601`).
2. **~~It is independent of FD-1356.~~ (Superseded 2026-10-01, 11:10:39 entry: DP-6's reset puts `gipricing`'s 10 rows at `review`, and they keep running, so it is not independent.)** Original text: FD-1356's reset (the follow-on 2, `RL 9750` DP-6) writes
   `review` onto an approved rule with no approved request, and that rule would keep running in
   its sets. But the maintainer's re-run of Task 0 measured `route_approved = 0` on every
   database (the 11:07:28 addendum), so **today that reset touches no row, and FD-1356's own
   discharge does not depend on this finding.** What remains is the gap whatever makes a member
   non-`approved`: a rule version bumped, a future un-approve or retire path, a row deleted, a
   restore, a fixture.
3. **The P2 exit demo walks it.** `WF-698` (dataset to approved model) and `WF-699` carry a
   Dataset Version from validation into model approval, which is FR-50's exact scope (the
   maintainer's reading, 11:07:12 entry). I read `WF-698`'s row at `:130`, "a rule set change later
   fails the version", and did not trace whether it is implemented.

## Evidence

**Code:** the trace above, at tree `49cd25be441382aebc1cc9c9ff325bd73fd81bc1`.

**Red reproduction: reasoned from code, not run.** A run needs the shared test database, whose
teardown truncates every table (F45). A red test: author a rule, walk it to `approved`, put it in
a Rule Set, move the rule row to `review` (a direct row write in the test), run validation on a
Dataset Version, and assert the run refuses with `RULE_NOT_APPROVED` or reports the member. Today
the run succeeds and the report cites the `review` rule. A second red test deletes the member's
rule row and asserts the run names the missing member; today it silently runs the rest.

**Exposure, measured 2026-10-01 at 11:08 BST (10:08 UTC), read-only,** `docker exec
gi-pricing-postgres-1 psql -U gipricing -d <db>` over every `gipricing%` database (80 listed),
each query inside `BEGIN READ ONLY … ROLLBACK`:

```sql
BEGIN READ ONLY;
with latest as (select distinct on (workspace_id, dataset_id) * from validation_rule_sets order by workspace_id, dataset_id, version desc),
m as (select l.id sid, coalesce(e->>'rule_id', e#>>'{}')::uuid rid, coalesce((e->>'enabled')::bool, true) en
      from latest l, jsonb_array_elements(case when l.body ? 'rules' then l.body->'rules' else coalesce(l.body->'rule_ids','[]'::jsonb) end) e),
j as (select m.sid, m.en, r.status, r.id is null as missing from m left join validation_rules r on r.id = m.rid)
select (select count(*) from latest), count(distinct sid) filter (where status is distinct from 'approved'), count(*) filter (where missing), count(*) filter (where status is distinct from 'approved' and not missing), count(*) filter (where status is distinct from 'approved' and en) from j;
ROLLBACK;
```

(`latest` is each dataset's newest set, the one `rule_set_for` reads.) Result over **77 databases
that have the two tables: 314 latest Rule Sets; 0 sets holding a non-`approved` or missing
member; 0 missing members; 0 non-`approved` members; 0 non-`approved` enabled members.** **No
local Rule Set holds a member that should not run today.** A control query over the same join
(count of members, and of members whose status is `approved`) returned **314 members, 314
`approved`**, so the join resolves rows and reads `status`: the zero is not an empty join.
**This measures the state before DP-6's reset:** the zero is today's, and the reset would add `review` members that still run. **Limits:** local databases only, the set moves as worktree databases come and go; 3 of the 80
databases are not counted (the first query ended in an error there; `gipricing_clone_m2` has no
`validation_rule_sets` table, the other two I did not inspect); only each dataset's newest set is
read, not older versions; and the zero cannot show that the filter fires on a non-approved row,
because none exists here to try it on.

## Severity (the maintainer's)

**MEDIUM, deadline before the P2 exit demo.** The path is real and reachable; no local database
shows an instance; there is no production.

## Owner (the maintainer's): WK-1178

## Disposition options (for a decision-maker; the maintainer: "a DM rules WHERE it is enforced")

1. **At the run.** `_to_rule_set` (or `rule_set_for`) refuses a set with a non-`approved` member
   and one whose members do not all resolve. The strongest guard: every validation, in every
   path, runs only approved rules. Cost: a set whose rule lost approval stops validating
   until fixed, which is the point, and the refusal needs a code (`RULE_NOT_APPROVED` is `01`'s
   own) and a spec line. It would also touch the dry-run of one rule, which must stay allowed for
   a `draft` rule (`data_handlers.py:241-244` builds its one-rule set without `rule_set_for`, so
   the split exists).
2. **At model approval, as an evidence check** for the Dataset Version's validation: its report's
   `rule_set_id`/`rule_set_version` names the set; refuse a model whose Dataset Version was
   validated against a set that held a non-`approved` rule. Matches FR-50's scope literally ("a
   Dataset feeding an `approved` Model") and leaves validation itself informative. Cost: a
   report would have to record each rule's status at run time, or the check reads the set at
   approval time, which can differ from the run's.
3. **Both.** The maintainer: FR-50's scope "suggests model approval at least, but that is the
   DM's call, with verbatim `01` text if the spec moves."

**The silent member drop** is ruled with whichever is chosen (the maintainer's addendum): the run
must refuse or report a set whose members do not all resolve to approved rules.

**Recommendation: option 3**, the run refusing (option 1, which also closes the silent drop) as
the primary guard and model approval reading the report's recorded rule status as the check
FR-50 names. Either alone leaves the clause half-enforced. The DM decides.

## Disposition

**Current (2026-10-01, the maintainer's 11:10:39 entry):** the remedy rides in the FD-1356 fix slice
(PL 9762). `dm-1356` rules where, in RL 9750 (the run, model approval, or both; the silent
missing-member drop is ruled with it, per the 11:07:28 addendum). **Discharge = the FD-1356 slice's
merge.** Filed by the auditor; the verdict is the lead's.

**Superseded (struck, kept for the record):** ~~Open. Not part of the FD-1356 fix slice (PL 9762): the reset it contains touches no row today; its own FD, deadline before the P2 exit demo, a DM rules WHERE (the maintainer, 11:07:12 and 11:07:28).~~
