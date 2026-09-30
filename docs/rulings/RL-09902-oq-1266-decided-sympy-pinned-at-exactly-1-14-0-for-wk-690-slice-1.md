---
id: RL-9902
family: ruling
title: OQ-1266 decided — sympy pinned at exactly 1.14.0 for WK-690 Slice 1
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 0bc69b5b2c3c16ec8391387cdfab19734ff85d2b
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-1266, RL-1265, PL-1268]
---

# RL-9902 — OQ-1266 decided: `sympy` is pinned at exactly `1.14.0` for WK-690 Slice 1

## How this was ruled

**Ruled at effort `medium`**, under the maintainer's decision by delegation of 2026-09-30
08:00:36 BST (`to-lead.md`, entry headed "08:00 CHECKPOINT DECISION: an interim
medium-effort pass for #937 and #946 ONLY; the rest wait for effort high"). That entry
reads: "The DM rules #937 (OQ-1266, the sympy pin) now, at medium effort", because "the
decision is evidence-determined". The decision-maker's role line sets effort `high` for a
ruling on the maintainer's raise; this pass is the maintainer's stated exception to it, and
is recorded as such. The record was prepared earlier at medium effort (PR #937, head
`06bfea84`, "PREPARED, NOT RULED"); this pass re-verified its evidence and rules it.

**Working id 9902.** The id is minted at the merge turn, which the lead schedules.

## Verified first, at 0bc69b5b2c3c16ec8391387cdfab19734ff85d2b

**The question** (`OQ-1266`; `docs/open-questions.md:119`, mirrored at `02` §10
`docs/specs/02-modelling.md:3247`): which exact `sympy` version does WK-690 Slice 1 pin?

**What the pin must satisfy.**
- `RL-1265`'s "The sympy pin" row (`docs/rulings/RL-01265-…md:190`): Slice 1 pins one exact
  version, and amends `02` §4.6 and §4.7 to cite it.
- `PL-1268` Slice 1 (`docs/plans/PL-01268-wk-690-expression-custom-objectives-map-plan.md:430-437`):
  §4.6 (`"derivation_version"`) and §4.7 (`library_versions.sympy`) "are amended, dated, to
  cite the exact version pinned in `uv.lock` (OQ-1266's answer)"; Gate 2 is "OQ-1266 is
  ruled: the exact `sympy` version to pin".
- `02` §4.6's example records `"derivation_version": "1.14.0"` (`02-modelling.md:1015`);
  §4.7's example records `"sympy": "1.13.x"` (`:1069`), a range.
- `uv.lock` and every `pyproject.toml` hold no `sympy` or `mpmath` at this tree:
  `git grep -n -i "sympy\|mpmath" 0bc69b5b -- uv.lock '*pyproject.toml'` → no output, rc 1.
- Prior certification: `docs/research/track-a-findings.md` F2 — the `where()` → `Piecewise`
  spike ran on SymPy 1.14.0, 2026-08-14. `docs/skills-map.md:67` reads "Verified on 1.14.0".
- Precedent for the pin form: `packages/pricing-core/pyproject.toml:9-13` pins
  `"hypothesis==6.165.7"` exactly, with a comment naming its authority.

**PyPI, queried 2026-09-30 08:01:50 BST** (`curl -s https://pypi.org/pypi/sympy/json`):
`info.version` = `1.14.0`, `requires_python >=3.9`. Its wheel
`sympy-1.14.0-py3-none-any.whl`, uploaded 2025-04-27T18:04:59, sha256
`e091cc3e99d2141a0ba2847328f5479b05d94a6635cb96148ccb3f34671bd8f5`, not yanked. No newer
release exists, so "current" is not reopened.

**The certification, re-run on the pinned version at this tree.** Scratch environment,
outside the repository and its lock:

```text
uv venv -q -p 3.12 $S/venv
uv pip install -q -p $S/venv/bin/python sympy==1.14.0     # resolved: sympy 1.14.0, mpmath 1.3.0
$S/venv/bin/python $S/spike.py                            # 2026-09-30 08:01:56 BST
```

`$S` = `/home/puzhenhao1989/.claude/jobs/0081b83b/dm-sympy-cert` (not committed). `spike.py`
is the prepared record's script, sha256 `0ab45a473db0285a…`. It takes §4.6's example
**exactly as the spec writes it** — the three strings were each matched once in
`02-modelling.md` at `0bc69b5b` by `git grep -c` (`"loss": …`, `"gradient": …`,
`"hessian": …`) — maps `where(c,a,b)` to `Piecewise((a,c),(b,True))`, differentiates the loss
twice in `f`, and compares with `simplify(piecewise_fold(derived − spec)) == 0` plus a numeric
check on both branches. Output, verbatim:

```text
sympy 1.14.0 python 3.12.13
gradient==spec True hessian==spec True numeric True
str(g) sha256 54c745bef45cbc21
str(h) sha256 fb8388e1dbc22d65
srepr(h) sha256 ce39a02d88f1287e
rc=0
```

The three hashes equal the prepared record's, taken 2026-09-30 00:48:23 BST on both 1.13.3
and 1.14.0. Behaviour on the spec's example does not distinguish the two lines; 1.13.3 was
not re-run in this pass, because the ruling does not rest on it.

## Ruled

**Option (a)+(c) of the prepared record: pin `sympy==1.14.0`, and the spec cites the lock,
not a literal.**

1. **The pin form.** WK-690 Slice 1 adds `"sympy==1.14.0"` to the `dependencies` of
   `packages/pricing-core/pyproject.toml` — the package that owns
   `pricing_core.data.expressions` — with a comment citing this record, as the `hypothesis`
   pin beside it does. `uv.lock` then resolves exactly one `sympy`, version `1.14.0`, and
   `mpmath` at whatever the lock resolves under sympy's own `mpmath<1.4,>=1.1.0` (1.3.0
   today). `sympy`'s only runtime dependency is `mpmath`, so `pricing-core` stays importable
   standalone with no FastAPI, SQLAlchemy or Redis dependency (`CLAUDE.md` §2). The pin is
   `==` in `pyproject.toml`, not only in the lock, because a certificate records the
   derivation version and an upgrade must be a deliberate, reviewed edit.
2. **Where the spec cites it.** In the same Slice 1 commit, and dated, per `RL-1265`'s pin
   obligation and `PL-1268` Slice 1:
   - `02` §4.6: the `derived.derivation_version` of the example is the pinned version; the
     prose states that it is the `sympy` version pinned in `uv.lock` (by this record), read
     at derivation time from `sympy.__version__`, never a literal in code.
   - `02` §4.7: the example's `library_versions.sympy` `"1.13.x"` becomes `"1.14.0"`, with
     the same citation of the lock.
   - `02` §8's SymPy row (`02-modelling.md:2842`) names the pin by citing `uv.lock`.
   - `docs/skills-map.md`'s SymPy row (`:67`) states the pin (`CLAUDE.md` §10: a tech
     dependency change updates it in the same PR).
3. **Why 1.14.0.** On the spec's own example the derivations are byte-identical on 1.13.3
   and 1.14.0, so behaviour does not choose. Then 1.14.0 is the only candidate with the
   project's own certification behind it (track-a F2, and today's re-run), it is what §4.6
   and `skills-map.md` already name, and it is PyPI's current release. §4.7's `1.13.x` has
   no recorded rationale in the tree.
4. **Why the lock is cited, not a literal.** The two literals disagreed because both were
   written with no pin to cite. A spec that cites `uv.lock`, and a certificate that reads
   `sympy.__version__` (`PL-1268` item 9), cannot drift from the pin again.

**Not ruled here.** Whether to widen the spike to the strict-profile refusal cases: those are
Slice 1's own refusal tests (`PL-1268` Slice 1, Gate outline), which exercise the pinned
version, so no separate spike is required before the slice.

**No `FR-` is appended.** The obligation this answer fills is already `RL-1265`'s ("Slice 1
pins one exact version and amends §4.6 and §4.7 to cite it"); this record supplies the
version. The spec text changes with the code, in Slice 1, because a spec citing a pin in
`uv.lock` before `uv.lock` holds it would state something false at its own tree.

## What it obliges

- **This commit:** `OQ-1266` is closed in both mirrors (`docs/open-questions.md` and `02`
  §10), citing this record.
- **The roadmap (the lead's file, not edited here):** the §10 row *Before WK-690 Slice 1*
  strikes `OQ-1266` and recounts to `1 (0 open)`. A decided question keeps its row.
- **WK-690 Slice 1 (`PL-1268` Slice 1, leaf plan now unblocked on Gate 2):** the pin, the
  §4.6/§4.7/§8 amendments and the `skills-map.md` row above, in one commit with the code.

## Acceptance — the violation that must become detectable

The violation: **the derivation version the platform records differs from the `sympy`
actually pinned.** Slice 1 (and Slice 2 for the certificate) carries the checks, each shown
red on deliberately broken input:
- *Violation: `uv.lock` resolves a `sympy` other than `1.14.0`, or more than one.*
- *Violation: a `derived.derivation_version` or `library_versions.sympy` is written from a
  literal rather than `sympy.__version__`* — a test running with a patched
  `sympy.__version__` must see the patched value recorded.
- *Violation: a `sympy` version literal remains in `02` §4.6/§4.7 prose other than as a
  citation of the lock* — checked at the Slice 1 review.
