---
id: RL-8283
family: ruling
title: FD-1959 closes at the merge of SL 8281 on its static limbs — the browser-verification limb (axe-core and Playwright) lives in OQ-1960, decided at the P2 close (R10-DP4 option (c))
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-29               # drafted 2026-10-29 under working id 8283
owner: decision-maker          # document-ids.md §1.6 RL row (RL-1958 the precedent); the lead's "2026-10-29 22:34:29 GMT" (b), confirmed in "2026-10-29 22:34:57 GMT", corrected the draft's `lead`
tree: 265a552ef3584eef22f506b9ffb001e8f3d27948
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1959, FD-8284, OQ-1960, PL-1546, SL-8281]
---

# RL-8283 — FD-1959 closes at the merge on its static limbs; the browser limb lives in OQ-1960

## Authority and scope

- **The ruling:** the maintainer's entry "2026-10-29 22:13:59 GMT — Maintainer: PL-1546 row 10 (FD-1959 — NFR-463 static limbs; SL 8281 / LG 8282) ACCEPTED at draft/pl-a11y @7e14e2e3" in `to-lead.md` (a local channel file, cited by its header), decision R10-DP4 (c). Verbatim:
  *"R10-DP4 (c) — an RL- minted in this slice's PR records THIS ruling: FD-1959 closes at the merge on its static limbs (F1–F3, M3, M4, the lows per DP2), and the browser-verification limb (axe-core + Playwright) lives in OQ-1960, decided at the P2 close; the FD's Disposition is amended by that RL, append-only, with the OQ cross-reference both ways."*
- **The question it answers** (PL-1546, decision point R10-DP4): FD-1959's Disposition reads *"The finding closes when F1 and the four moderates are fixed and their tests are green on `origin/main`, the lows are fixed or carried with a date, and OQ-1960 is decided."* OQ-1960 is decided at the P2 close, after the fix merges. Options: (a) the PR discharges the fix limb by a dated line and FD-1959 stays open on its carried limb; (b) rule OQ-1960 now; (c) amend the Disposition so FD-1959 closes at the merge. The maintainer ruled (c).
- **Related rulings read with it:** R10-DP2 (a) — the lows that are not one line are carried, owner WK-675, to the P2 close with OQ-1960; R10-DP1 (b) — F2's scope. Neither is changed here.
- **The tree:** read at `draft/sl-8281` head `265a552ef3584eef22f506b9ffb001e8f3d27948` (`git ls-remote origin draft/sl-8281`). Nothing was executed.

## Ruled

1. **FD-1959 closes at the merge of SL 8281 on its static limbs:** F1, F2, F3, M3, M4, and the lows as R10-DP2 sets them (F5, F6, L11, L12 fixed; F4, L4, L5, L6 to L10 carried, and the accessibility-tester's two new lows at the head carried by the lead's disposition of 2026-10-29). **The ten carried lows are the rows of FD-8284** (owner WK-675, LOW, due Thu 12 Nov 2026, the P2 exit demo), minted in the PR of SL 8281 on the lead's "2026-10-29 22:34:57 GMT" ruling (a); it is their home once FD-1959 is closed.
2. **The browser-verification limb** (rendered contrast, focus order, screen-reader announcements, Focus Not Obscured 2.4.11, reflow, text spacing, target size — FD-1959's "Carried limb: the static-only limit") **lives in OQ-1960 only.** Whether `axe-core` and Playwright enter `frontend/package.json` is decided there, owner WK-675, at the P2 close. A "yes" changes `docs/skills-map.md` in the same PR (`CLAUDE.md` §10).
3. **FD-1959's Disposition is amended by this record, append-only.** The original sentence stays; the essay gains a dated line citing RL-8283 (see "What it obliges").
4. **The cross-reference runs both ways:** FD-1959's essay and register row name OQ-1960 and RL-8283; OQ-1960's row (in `docs/open-questions.md` and the `00-overview.md` §10 mirror, both) names FD-1959's closure by RL-8283 and says the browser limb is now held only there.
5. **What this does not change:** NFR-463 (`docs/specs/00-overview.md:586`) is unchanged; WK-675's acceptance still reads OQ-1960 and the carried lows (the maintainer's acceptance is the maintainer's alone, `CLAUDE.md` §13); no dependency is added by this record.

## What it obliges

- The slice PR that merges SL 8281 carries: the FD-1959 essay Disposition amendment and its `***Resolved***` paragraph; the register row's Resolved text, appended inside the row's last cell with the opener kept; the essay and register carry lines naming FD-8284 for the ten carried lows (owner WK-675, due Thu 12 Nov 2026); `status: closed` on the essay in place; and a regenerated `docs/INDEX.md` after the mint (seat brief item 17).
- **WK-675's close record lists FD-8284 (the ten carried lows) and OQ-1960 as carried forward** (R10-DP2 (a)). With FD-1959 closed, FD-8284 is the carried lows' home and the close record lists it; "unowned" is not a permitted state (`CLAUDE.md` §14).
- OQ-1960 stays open and unchanged in substance; only the cross-reference line is added.

## The carry date

R10-DP2 (a) named "the P2 close" without a calendar date; the lead's "2026-10-29 22:34:57 GMT" ruling (a) names it: **Thu 12 Nov 2026**, the P2 exit demo (`date -d 2026-11-12 +%A` prints Thursday), recorded in FD-8284.
