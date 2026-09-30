---
id: RL-9902
family: ruling
title: PREPARED, NOT RULED — the exact sympy pin for WK-690 Slice 1
status: draft                  # NOT a permitted RL status (§1.2: active → superseded | retired); deliberate, see "Status of this record"
created: 2026-09-30
owner: decision-maker
tree: aa14e90dd77c7461aa35cc6461557b129959463f
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-1266, RL-1265, PL-1268]
---

# RL-9902 — PREPARED, NOT RULED: the exact `sympy` pin for WK-690 Slice 1

## Status of this record — read this first

**Nothing here is ruled.** This is a *prepared* ruling, written at effort `medium` under the
maintainer's decision by delegation of 2026-09-30 00:42:01 BST (`to-lead.md`, entry headed
"#933 READ BACK; DECISION: the DM PREPARES the blocked rulings on medium now, and RULES only
on effort high"). The open question it prepares stays **open**, no spec text is amended, the
roadmap §10 gate "Before WK-690 Slice 1" stays open, and **WK-690 Slice 1 does not start on
it**. The ruling is the later pass at effort `high`.

**`status: draft` is not a status a ruling may carry** (`document-ids.md` §1.2, RL:
`active → superseded | retired`; `scripts/audit-docs.py` check 33). It is kept on purpose so
the gate refuses this file as a ruling; the ruling pass sets `active` and mints the id.

**Ids.** When this record was drafted, the open question, the ruling that filed it and the
map plan were unminted (working ids 9660, 9202, 9103), so it cited them in prose. All three
have since minted, and this refresh cites them by real id: `OQ-1266`, `RL-1265`, `PL-1268`.
Working id 9902 (this record) was checked free on `origin/main` and every `origin/*` branch.

*Refreshed 2026-09-30 onto main `0bc69b5b2c3c16ec8391387cdfab19734ff85d2b`. Each deciding-evidence
claim below was re-checked there. `uv.lock` and every `pyproject.toml` still hold no
`sympy`/`mpmath` (rc 1). `02:1015`/`:1069` still carry `1.14.0`/`1.13.x`. PyPI's latest is
still `1.14.0`. The spike is not re-run: the wheels and the spec example are unchanged.*

## Verified first

**The question** (`OQ-1266`; `docs/open-questions.md:119` and `02` §10 `02-modelling.md:3247`): which exact `sympy` version does WK-690 Slice 1 pin?

**What the pin must satisfy.**
- `RL-1265`'s DP-5 obligation (its "The sympy pin" row): Slice 1 pins **one exact** version
  and amends `02` §4.6 and §4.7, dated, to cite it.
- `PL-1268`, item 9 and Slice 1's Gates: Slice 1's leaf plan is filed only when the question
  "is ruled: the exact `sympy` version to pin"; Slice 2 records the version on the
  certificate from `sympy.__version__`, never as a literal.
- `02` at `origin/main` `aa14e90d`: §4.6's example records `"derivation_version": "1.14.0"`
  (`docs/specs/02-modelling.md:1015`); §4.7's records `"sympy": "1.13.x"` (`:1069`) — a
  range, not a version. The certificate's `_note` calls its figures illustrative.
- `git grep -n -i "sympy\|mpmath" origin/main -- uv.lock '*pyproject.toml'` → rc 1, no hits.
  Nothing in the tree constrains the choice.
- Prior evidence: `docs/research/track-a-findings.md` F2 (`:15`, `:62`) — the `where()` →
  `Piecewise` certification spike ran on SymPy **1.14.0**, 2026-08-14.

**Empirical, run 2026-09-30 00:48:23 BST** (not committed; script and log at
`/tmp/dmprep-sympy/spike.py` and `spike-1790725703.log`, reproducible from the method here):
- PyPI JSON (`https://pypi.org/pypi/sympy/json`): `info.version` = **1.14.0** (uploaded
  2025-04-27, `requires_python >=3.9`); the 1.13 line ends at **1.13.3** (2024-09-18,
  `>=3.8`); none yanked. Both require `mpmath<1.4,>=1.1.0`; `mpmath 1.3.0` used.
- Wheels fetched without pip (`library-spike`): `sympy-1.13.3-py3-none-any.whl` (sha256
  prefix `54612cf55a62755e`), `sympy-1.14.0-py3-none-any.whl` (`e091cc3e99d2141a`).
- Spike: §4.6's example objective taken **exactly as the spec writes it** (`loss`, and the
  `derived.gradient` / `derived.hessian` strings), `where(c,a,b)` → `Piecewise((a,c),(b,True))`,
  differentiated twice in `f`, run under the repo's venv interpreter (Python 3.12.13,
  `uv run --no-sync python`). Both versions: gradient and hessian equal the spec's
  (`simplify(piecewise_fold(derived − spec)) == 0`) and agree numerically on both branches;
  rc 0. **The outputs are byte-identical across the two versions**: `str(gradient)` sha256
  prefix `54c745bef45cbc21`, `str(hessian)` `fb8388e1dbc22d65`, `srepr(hessian)`
  `ce39a02d88f1287e`, the same under 1.13.3 and 1.14.0.

**What the spike means:** on the spec's own example, library behaviour does **not**
distinguish the two lines. The choice turns on provenance and currency, not on derivation
output. One example is not the grammar; the ruling pass may want the spike widened to the
strict-profile refusal cases Slice 1 builds.

## Options

| | Option | For | Against |
|---|---|---|---|
| (a) | **Pin `1.14.0`**; §4.7's `1.13.x` corrected to agree | The newest release on PyPI at the time of the query; the version the 2026-08-14 certification spike verified (track-a F2) and that §4.6 already names; today's spike reproduces §4.6's derivatives on it | A literal in the spec can drift from the lock again, as the two literals already have |
| (b) | **Pin `1.13.3`** (the last `1.13.x`); §4.6 corrected to agree | Matches §4.7's range | An older, superseded line; nothing in the tree says why §4.7 named it; the derivation evidence on record is for 1.14.0 |
| (c) | **Choose at Slice 1 by spike; spec cites `uv.lock`, not a literal** (the question's own recommendation) | The spec cannot disagree with the pin again | Defers the choice past the gate: `PL-1268`'s Slice 1 gate asks for "the exact `sympy` version to pin", which (c) alone does not give |
| (a)+(c) | **Pin `1.14.0` now, and word the §4.6/§4.7 amendments to cite `uv.lock`** (certificate reads `sympy.__version__`, per `PL-1268` item 9) | Satisfies the gate with an exact version **and** removes the drift that caused the question | None found at medium; the ruling pass should confirm the amendment wording is Slice 1's, per `RL-1265` DP-5 |

## Provisional recommendation — (a)+(c), not ruled

**Pin `sympy==1.14.0`** (with `mpmath` resolved by the lock under `<1.4`), and have Slice 1's
§4.6/§4.7 amendments cite the version in `uv.lock` rather than restate a literal.

**The one piece of evidence that decides it:** the spike shows byte-identical derivations on
1.13.3 and 1.14.0, so behaviour does not choose — and 1.14.0 is then the only candidate with
the project's own certification evidence behind it (`track-a-findings.md` F2, SymPy 1.14.0)
as well as being PyPI's current release.

**Left for the ruling pass at effort `high`:** (1) re-query PyPI (a newer release would reopen
"current"); (2) whether to widen the spike to the strict-profile cases; (3) which
`pyproject.toml` carries the dependency (`pricing-core` must stay importable standalone —
`sympy` has only `mpmath` as a runtime dependency, which that rule permits) and whether the
pin is `==` in `pyproject.toml` or exact only in `uv.lock`; (4) Slice 1's `docs/skills-map.md`
row (`CLAUDE.md` §10), which the question's recommendation already names.

## Ruled

**Nothing.** This heading is present because check 37 requires it of the ruling family. It
records no decision.

## What it obliges

**Nothing, and nobody.** No slice starts on this record; no spec, open-question, roadmap or
plan text is changed by it. The open question stays open.

## Acceptance — the violation that must become detectable

*Provisional, for the ruling pass.* If (a)+(c) is ruled: `uv.lock` resolves exactly one
`sympy`, `1.14.0`; a certificate whose `derivation_version` differs from the running
`sympy.__version__` is detectable (a test fails); and no `sympy` version literal remains in
`02` §4.6/§4.7 other than a citation of the lock.
