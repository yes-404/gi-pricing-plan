---
id: RS-8235
family: research
kind: audit
title: SL-8178 (WK-1178 delta) delta audit, 1d06b46b to 91c5ed06 — the slice's own docs delta and RS-8214's B-items
status: draft
created: 2026-10-25
owner: auditor
tree: 91c5ed06da26e2c4af07342f67fb3ba6b4ab17c3
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-8178, LG-8179, RS-8214]
---

# RS-8235 — SL-8178 delta audit, 1d06b46b → 91c5ed06

*(Working id 8235, written by `aud-8178d`, 2026-10-25 19:1x GMT, from `brief-aud-8178d-2026-10-25.md` (lead 28). Check 31/32 on this id and on SL-8178, LG-8179 are expected until the mint. Tree audited: `91c5ed06da26e2c4af07342f67fb3ba6b4ab17c3` (gate head of record, branch `fix/fd-8175-resource-backed-guard`); `origin/main` at writing is `ef3ac6c8`. Docs-only read; no test, gate or audit-docs run — those are owed.)*

**Verdict PROPOSED (the lead's to adopt): CLEAN.** The gated code is the audited code, every own-docs change is in scope, and RS-8214's B1 and B2 (and B3, B4) are landed in LG-8179 as appended lines.

## Authority

To-lead `## 2026-10-25 19:07:02 GMT — Maintainer: FD 8194 + SL 8178 ACK paths → option (a) written delta audits (8234, 8235)…`: "**RULED (a):** one docs-only sonnet auditor seat per slice … scope = the slice's own docs delta audited head → gate head + the patch-id equality quoted + **verification that RS 8213's B1/B2 and RS 8214's B1/B2 are landed as dated LG lines**". RS 8213 belongs to FD 8194's slice (RS 8234); this record covers RS 8214 only.

## 1. Code: patch-id equality

Predicate: `git -C <wt> diff $(git -C <wt> merge-base <h> origin/main) <h> -- . ':!docs' | git patch-id --stable`, run in the aud-8178d worktree.

| head | merge-base with origin/main | non-docs patch-id |
|---|---|---|
| `1d06b46b` | `4e399fd01e8de2fe55d2f128b0e09ee2b2735c6a` | `8f501517c05f85a9ec9b03dab8a454f36d37a10b` |
| `91c5ed06` | `01a28e6d5571ed8f8d478760fc11aa2015326840` | `8f501517c05f85a9ec9b03dab8a454f36d37a10b` |

Equal. The gate head carries the audited head's code unchanged.

## 2. The slice's own docs delta

`git diff --name-only 1d06b46b 91c5ed06 -- docs` lists 22 paths; most are main's merge (#1368–#1376). The slice's own docs delta is the diff of each head against its own merge-base (`git diff <mb> <h> -- docs`, `--name-only`): at `1d06b46b` {INDEX.md, LG-08179, roadmap.md}; at `91c5ed06` the same plus `RS-08214`. Main-origin paths (specs 02/03, contracts, findings, other LG/RS, register) are not the slice's.

| path | verdict |
|---|---|
| `docs/ledgers/LG-08179-…md` | IN SCOPE. `git diff 1d06b46b 91c5ed06` = one hunk `@@ -56,3 +56,22 @@`, 19 added lines, 0 removed: two appended sections ("Corrections and strict red run", "Strict RED evidence form"), each headed with its date and "appended; earlier lines unchanged". Append-only holds. |
| `docs/research/RS-08214-…md` | IN SCOPE. New file (77 lines) — the previous audit, folded onto the branch (brief item 34). Not on main. |
| `docs/INDEX.md` | IN SCOPE. The slice's own rows at `1d06b46b`: SL-8178, LG-8179; at `91c5ed06` plus RS-8214. Everything else in the INDEX diff is main's rows. Regenerated and checked below. |
| `docs/roadmap.md` | IN SCOPE. The slice's own hunk is identical at both heads (20 added lines, the SL-8178 block, `status: active`); the other roadmap lines differing between the two heads are main's. |

## 3. RS-8214's B-items against LG-8179 at `91c5ed06`

| item | RS-8214 (quoted) | LG-8179 line | status |
|---|---|---|---|
| B1 | "a verbatim quote in the LG was altered by the id re-point … `**GO:**` line quotes … 'It goes in the FD-1851 close vehicle' … the entry reads 'FD 8175 close vehicle'. Fix: an appended line …" | line 64: "**B1.** The GO line's quotation above reads "It goes in the FD-1851 close vehicle", a re-point made inside quotation marks. The verbatim form is "It goes in the FD 8175 close vehicle" [FD 8175 = FD-1851 at the mint]." (GO line 21 itself unedited) | LANDED |
| B2 | "LG Scope paragraph is stale. … FD-1851 is `retired` on main … the line stays, the append says it is discharged." | line 65: "**B2.** "FD-1851's own close is owed" is stale: FD-1851 is `status: retired` on main (`docs/findings/FD-01851-…md`, front matter …)." I checked `git show origin/main:` that file: `status: retired`. | LANDED |
| B3 (note) | the "2 warnings" are two different warnings | line 66 | LANDED |
| B4 (note) | "three entries" is the base count; main has five | line 67 | LANDED |

Date form: the four lines sit under the heading at line 60, "(exec-8178r, 2026-10-23 11:58 BST, appended; earlier lines unchanged)"; the lines carry no date of their own, the section heading does. I read that as "dated LG lines". Lead's call if per-line dates are wanted.

RS-8214's out-of-slice point (RL-1848 quotes its entry heading as "RL-1848 ADOPTED", not "RL 8176 ADOPTED") is not this slice's write set and remains for the lead to route.

## 4. Checks run and owed

Run: patch-id pair, diff/name-only reads, `git show origin/main:` of FD-1851. INDEX regenerate and `--check`: see the report. Owed (no grant for this brief): audit-docs, the docs-audit pytest set at the mint, check 31/32 on ids 8178/8179/8214/8235 at their mint.
