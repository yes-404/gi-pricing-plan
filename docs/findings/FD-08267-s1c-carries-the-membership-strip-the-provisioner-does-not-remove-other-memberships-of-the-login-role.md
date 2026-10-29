---
id: FD-8267
family: finding
title: S1c carries the membership strip — the provisioner does not remove other memberships of the login role
status: active
created: 2026-10-29
owner: WK-1178
tree: e239733c1477c5ab0e8d4c897638767cb4c3e0b9   # origin/draft/s1c-fd1951 as read by the auditor, 2026-10-29
corrected_by: []
relates: [FD-1951, SL-8266, LG-8269, PL-1927]
---

# FD-8267 — S1c carries the membership strip: the provisioner does not remove other memberships of the login role

## Finding

**MEDIUM; owner WK-1178.** Authority: the maintainer's entries "2026-10-26 13:12:34 GMT — DP-S1c-1 RULED" (item 4, split) and
"2026-10-26 13:50:37 GMT" Q3 (`to-lead.md`): the strip of other memberships is CARRIED by FD-1951 to WK-1178, and its `FD-` is
written by S1c's auditor, inside S1c's PR, so FD-1951 closes with the limb in a record. Filed under working id 8267.

`deploy/postgres/app-login-role.sql` at S1c's head converges `gip_app` (`:20`), states the membership `GRANT gip_app TO
gip_app_login WITH INHERIT TRUE, SET FALSE` (`:36`) and resets both roles' settings. It does **not** revoke any other membership
of `gip_app_login` or `gip_app` that a deployer or an operator granted by hand (for example `GRANT gipricing TO gip_app_login`).

## What the limb is, and where FD-1951 carried it

FD-1951's fifth medium: "Memberships and role settings are not reset ... A hand-granted owner membership stays (the startup check
refuses it; the provisioner does not undo it)". PL-1927 S1c-4 item 4 split it: the settings reset is in S1c (done: `RESET ALL`,
`IN DATABASE` rows, `VALID UNTIL 'infinity'`, `CONNECTION LIMIT -1`); "the strip of other memberships **carried by FD-1951 to
WK-1178**, because revoking memberships the deployer granted can break an operator's setup and the startup refusal already
catches every owner-reachable one."

## Why MEDIUM

- The residue is not a route to the owner at startup: `P_OWN` (`backend/src/app/db/immutability.py`) refuses any role that reaches
  an owner, a superuser, CREATEROLE, a predefined role, `session_replication_role` or a guard-function or schema owner, and on
  PostgreSQL 16 any `pg_auth_members` row counts as `MEMBER` (the S1c-4 correction, probes of 2026-10-26). A harmful leftover
  membership therefore stops the process, loudly.
- What the strip would add is convergence: a provisioned role set that holds exactly one membership. Without it, a harmless
  but unexpected membership (a role reaching nothing privileged) stays, and a refused one is repaired by the operator, not the
  provisioner. This is a defence in depth gap, not a silent mispricing path. Revoking is also an act on an operator's setup,
  which is why it was not taken blind.

## Remedy

A follow-up under WK-1178 that decides, with a ruling, whether the provisioner revokes every membership of `gip_app_login` and
`gip_app` other than `gip_app -> gip_app_login`, or only reports them: red-first on a planted extra membership, read back from
`pg_auth_members` before and after, with the operator-impact line (a deployer-granted membership is removed). The date: **fix before WK-1178's close, by the P2 exit demo Thu 12 Nov 2026 (lead 29, from-lead 2026-10-29 14:34:00 GMT).**

## Provenance

FD-1951 (S1b Step 7.2 postgres-pro review, fifth medium); the rulings above; S1c = SL 8266, ledger LG 8269, branch
`draft/s1c-fd1951` read at `e239733c`.

## Disposition

Open, owner WK-1178, MEDIUM. Filed under working id 8267.
