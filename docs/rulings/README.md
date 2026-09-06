---
family: reference
title: docs/rulings — one decision per file
status: active                  # active → retired (§1.2a)
created: 2026-09-06
owner: lead
corrected_by: []
relates: []                      # ids only
---

# docs/rulings — one decision per file

An `RL-` record is a decision taken while work was in flight: what was ruled, on what
question, with the reasoning that produced it and the date it was made. One ruling per file,
the padded id leading the filename.

**A ruling is not an ADR.** An ADR records an architectural choice that constrains more than
one module and is expensive to reverse ([`../adrs/`](../adrs/README.md)); a ruling settles a
question a slice ran into — scope, a signature, which of two readings of a requirement is the
operative one. A ruling that turns out to constrain the architecture becomes an ADR, and says
so.

**The reasoning travels with the decision.** A ruling recorded without the reason it was taken
is an instruction to reverse it the first time someone re-derives the obvious answer the
ruling rejected. Write the rejected reading down.

[`../INDEX.md`](../INDEX.md) is the index.
