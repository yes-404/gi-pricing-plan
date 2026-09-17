---
id: RL-904
family: ruling
title: RFC-843's "remove the relay" lands in `delivery-process.md` §15
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md
---

### RL-904 — RFC-843's "remove the relay" lands in `delivery-process.md` §15

**Ruled: immediately after §15's existing third bullet**, the one that already states
*"Verify against the primary source; never implement against a relay."*

The two are one rule with two halves, and separating them is what let the weaker half land
alone in the first place. The existing bullet says **do not trust a relay**; this says **do not
create one**. A reader who finds only the first concludes the fix is more careful reading,
which is precisely the conclusion RFC-843's eight instances refute — the lead was reading
carefully each time.

---
