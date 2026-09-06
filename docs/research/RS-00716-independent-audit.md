---
id: RS-716
family: research
kind: audit
title: Independent audit —
status: closed                  # draft → active → closed | retired (§1.2a)
created: 2026-08-15
owner: auditor
corrected_by: []
relates: []                     # ids only — the FR-/ADR-/RFC- target a spike's `closed` cites
was: docs/audit/closure-records.md
---

### Independent audit — 2026-08-15, and what it changed

Five auditors ran over Phase 1a's closed work, none of them allowed to read the closure
records they were auditing: each derived what should exist from the specs and then went
looking. The maintainer asked for it after noticing that every audit so far had been a
self-audit — every one of these five PRs merged with **zero reviews**.

**No security holes.** Separation of duties holds in three independent layers, workspace
isolation refuses cross-tenant ids indistinguishably from missing ones, secrets are never
returned, the dev identity grants no permissions and never reaches the production bundle.

**The finding was consistent across all five: the code mostly does what it says; the
records and checks claimed more than they establish.**

| Claim | What was true |
|---|---|
| "38 of 38 catalogue rules" | the check counted ids **in prose**; one docstring reading `VR-ACT-1/2/8` became three, two of which appear in no source file. The truthful count is 1, and that one is an error message |
| "all 7 of `01` §5.3's views" | true of the router; **6 of their 27 Contents items** are missing — lineage graph, histograms, PSI selector, status badge, last validated, owner |
| the frontend contract-drift check | ran `git diff` on a git-ignored path that CI creates in the same step. It could not fail |
| "a renamed heading breaks the guide loudly, and the test is in the gate" | it did not: two specs were covered by accident, five and the roadmap by nothing |
| FR-39's refusal, FR-42's immutability | specified, cited, and enforced nowhere |
| pandera as the Layer-1 mechanism | named in four places; a dependency of nothing |

**Three tests proved nothing**, shown by injection: authorisation was tested on three of
fifty-nine operations and a downgraded permission left all 609 green; the acknowledge route
had no HTTP test and swapping its two path parameters passed; the determinism fixture held
one rule, so randomising result order passed.

**What it changed**, in two commits:

- **Tier 1** (`fix/audit-tier-1`) — the checks that could not fail, and the tests that
  proved nothing. Each fix demonstrated against the injection that used to pass.
- **Tier 2** — this spec upgrade. The specs now describe what was built (pandera withdrawn,
  the rule-format params corrected, the reference publish lifecycle declared, `06`'s
  authentication-only routes stated, §5.2's signatures corrected) and carry the two
  obligations the code does not meet as **FR-40** and **FR-43**, unevidenced and
  owned by **WK-664** — and **delivered the same day** as Phase 1a's exit gate (plan review 2).
  Artifact immutability stopped being a convention on 2026-08-15.

**Tier 3, done 2026-08-15: the closure records for WK-660, WK-663 and WK-667 are rewritten.** Each had
measured a proxy — a route exists, a marker exists, an id appears — and reported it as the
thing. The corrections are made *in place with the original claim shown*, not by quietly
restating the record: WK-660's "38 of 38 catalogue rules" against what the check now reports,
WK-663's seven views against §5.3's twenty-seven Contents items, WK-667's "a renamed heading
breaks it loudly" against the auditor's rename that it did not catch.

The old wording is kept beside the correction on purpose. A record that silently becomes
right destroys the evidence of what was believed, which is the thing `CLAUDE.md` §0 says a
governed system cannot afford to lose — and these records exist to be the evidence.

`CLAUDE.md` §14 now makes the specification the plan review's main target at every stage
boundary, for the reason this audit demonstrated: a divergence left in a spec is a defect
the next workstream inherits and builds on.
