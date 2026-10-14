---
id: FD-1729
family: finding
title: The application never connects as gip_app; it connects as the superuser table owner, so every grant and revoke in FR-44's privilege layer is inert at runtime
status: active
created: 2026-10-14
owner: auditor
tree: a3fc2e8dd384de6abf909f662f43011b8078fb4e
corrected_by: []
relates: [WK-1178, FD-1704, FD-1728, FR-44, FR-43, P2]
---

# FD-1729 — the privilege layer binds no one

*(Minted 2026-10-14 as FD-1729 from working id 8038, in the D17 batch mint PR.)*

*(Filed under working id 8038, reserved by the lead. The code and compose predicates were run by the auditor at
`origin/main` `a3fc2e8dd384de6abf909f662f43011b8078fb4e` on 2026-10-14, from the object database, not the root checkout's
working tree; the role attributes were read from the shared Postgres container the same day. The counts and outputs below
are those runs', quoted, with the commands.)*

## Authority

The maintainer (by delegation), `to-lead.md`, "2026-10-14 12:00:14 BST", point (B), verbatim: *"**(B) A SECOND NEW FD,
proposed HIGH, the root cause under both:** verified at origin/main, `git grep -n -E 'gip_app|APP_ROLE|SET (LOCAL )?ROLE' --
backend/src deploy` = 0 hits. `gip_app` exists only in migrations (APP_ROLE = "gip_app", e.g.
a1b2c3d4e5f6_artifact_append_only.py:36). The app's DSN default is `gip` (backend/src/app/config.py:120) and compose's is
POSTGRES_USER `gipricing` (deploy/docker-compose.yml:13), i.e. the OWNER. **So every REVOKE/GRANT in FR-44's privilege layer
is inert at runtime,** including FD 8007's planned revoke on `factors`; only triggers bind. FR-44's "both layers" is not met
in any deployed topology. Owner: WK-1178, fixed in P2."* And, in the same entry, the planner's decision point: *"the owner
can still `ALTER TABLE … DISABLE TRIGGER`, so S-b is what makes the trigger layer tamper-resistant; state that dependency in
the FD."*

## Finding

**Proposed severity: HIGH, owner WK-1178, fixed in P2** (the auditor proposes; the lead and the maintainer (by delegation)
rule; the 12:00:14 entry names HIGH). FR-44 (`01-data-management.md:106`) says every artifact table carries two layers: a
privilege layer (grants to `gip_app` of `SELECT, INSERT` only) and a trigger layer (FR-43), and it records why both:
"revoking `UPDATE` from the *owner* does nothing — ownership carries implicit privileges". The privilege layer protects
only a connection that is `gip_app`. **No connection the application makes is `gip_app`**, and the connection it does make
is a superuser that owns every table. The privilege layer is therefore inert in every topology this repository deploys, and
the trigger layer is the only thing that binds, on the tables that have one, against a role that can switch it off.

## Evidence

**1. Nothing in the application or the deployment names the role.**
`git grep -n -E 'gip_app|APP_ROLE|SET (LOCAL )?ROLE' a3fc2e8d -- backend/src deploy` prints **0 lines** (run by the auditor
at `a3fc2e8dd384de6abf909f662f43011b8078fb4e`, 2026-10-14; the same predicate as the entry's, verbatim). `gip_app` appears
only in migrations and tests.

**2. The connection the application makes is the owner.**
- `backend/src/app/config.py:120`: `database_url: SecretStr = SecretStr("postgresql+asyncpg://gip:gip@localhost:5432/gip")`,
  the default DSN; its user is `gip`, not `gip_app`.
- `deploy/docker-compose.yml:13`: `POSTGRES_USER: gipricing` (with `POSTGRES_DB: gipricing`, `:15`). The image's bootstrap
  user is the role that creates the database and runs the migrations, so it owns every table (the catalog extract in
  FD-1728 shows `owner = gipricing` on all sixty public tables).
- The migrations run as that same role (`alembic` with `GIP_DATABASE_URL=…gipricing:gipricing@…`, `dev-commands`), so the
  application and the migrations are one role.

**3. The owner is a superuser.** Re-measured by the auditor on the shared container, 2026-10-14:
`docker exec gi-pricing-postgres-1 psql -U gipricing -d postgres -Atc "select rolname, rolsuper, rolcreaterole from pg_roles
where rolname in ('gipricing','gip_app')"` printed

```
gipricing|t|t
gip_app|f|f
```

`gipricing` has `rolsuper = t` and `rolcreaterole = t`; `gip_app` has neither. (planner-pl8016r measured the same at
12:07:50 BST on this container, per the lead.) This container is the local development database; a production topology
is not described by any file in the repository, and none of its files provisions a non-owner login role either, so no
topology can be shown in which the privilege layer binds.

**4. What the privilege layer would refuse, if it applied.** In the auditor-fr44 run (`~/.claude/jobs/b6860f8f/tmp/fr44/out4.txt`,
`8eaf6d5f`), `SET LOCAL ROLE gip_app` then `DELETE` or `TRUNCATE` on each of the ten FD-1728 tables, on `rating_versions`
(`DELETE`) and on `factors` (`DELETE`, `TRUNCATE`) was `ERROR: permission denied for table …`. The same statements as the
owner succeeded (FD-1728's table). The layer works; no one is subject to it.

## What this makes inert

- **Every `GRANT` and `REVOKE` in the migrations** (`a1b2c3d4e5f6_artifact_append_only.py:36` onward; `GRANT SELECT, INSERT`
  on the append-only tables; `GRANT SELECT, INSERT, UPDATE ON models, factors`, `b2c3d4e5f6a7_model_fit_immutable.py:89`).
  The "grants alone" tables FR-44 itself lists as not protected against a direct connection are protected against nothing.
- **FD-1704's planned `REVOKE UPDATE` on `factors`** (a limb of FD-1728): a revoke from `gip_app` changes nothing for a
  connection that is the owner. The trigger on `factors` is what must bind, and only S-b makes the revoke matter.
- **`test_artifact_immutability.py`'s grants-derived list** (FD-1728): it tests the grants, not what the application can
  do, so it stays green over an application that is not subject to them.

## Tamper limb: the trigger layer can be switched off by the role the application is

Because the application is the owner and a superuser, the trigger layer FR-43 relies on is also reachable. Two routes, each
available with the credentials the application already holds:

1. `ALTER TABLE <table> DISABLE TRIGGER <name>` (or `DISABLE TRIGGER ALL`): a table owner may disable its own triggers.
2. `SET session_replication_role = replica`: superuser-only, and the application role is one; it suspends every user
   trigger for the session. The test fixtures use exactly this for seeding (`conftest_db.py:~340`, "`session_replication_role
   = replica` suspends every user trigger at once"), and the auditor-fr44 seed did too; it is a documented, available
   mechanism, not a hypothetical.

A trigger-only fix (FD-1728's S-a) therefore closes the **accidental and ordinary-code** paths (an `UPDATE` anywhere in the
application that was never meant to run), and is effective even for the owner, so it closes the live risk fastest. It does
**not** close a deliberate write by the application's own role, a compromised application credential, or a migration or
hot-fix script run as the owner. **S-b (least privilege) is what makes S-a tamper-resistant**: once the application connects
as a role that is not the owner and not a superuser, it can neither `DISABLE TRIGGER` nor set `session_replication_role`, and
FR-44's privilege layer begins to bind. S-a without S-b leaves the dependency this section states.

*2026-10-14: per the maintainer's (by delegation) "2026-10-14 14:59:13 BST — Host exposure CLOSED: the user's read-only GCP check shows NO internet reachability of 5432/6379/9000/9001/8080 (re my 12:42:33)" (`to-lead.md`) — the measurement: network `default` has 4 ingress rules, all priority 65534: "default-allow-internal (10.128.0.0/9, all), -ssh (0.0.0.0/0 tcp:22), -rdp (0.0.0.0/0 tcp:3389), -icmp"; "no rule targets the VM's service account; no network firewall policies; no org/folder"; "live probe from outside GCP: 5432, 6379, 9000, 9001 and 8080 closed/filtered, with 22 OPEN as the control." "So the services are reachable only from inside the VPC (10.128.0.0/9)." Exposure of the superuser database recorded here: VPC-internal only, 2026-10-14. "No running container is recreated. S-b's Step 1.5 (compose binds every port to 127.0.0.1, red first) STAYS as defence in depth (other VMs in the VPC could reach them, and a future permissive rule would expose a superuser DB), together with the non-default GIP_APP_DB_PASSWORD gate (R8)."*

## The fix, for the planner (as ruled; a DP for the shape)

S-b as ruled at "2026-10-14 12:00:14 BST": the application connects as a login role with `gip_app`'s grants (the DSN,
compose provisioning), migrations still run as the owner, a startup and test assertion that `current_user` is **not** the
owner of the artifact tables, and the existing grants audited so the application can still do every write it legitimately
makes, red-first per refused path. Three facts the planner needs, from the runs:

- **The ten FD-1728 tables carry no `gip_app` grant at all** (`ins = f` on every one). An application running as `gip_app`
  today could not insert a rate table, a rate table version or its cells, a rating algorithm or a reference row. S-b's
  grants audit is therefore not a formality; it adds grants for those inserts, and S-a's triggers must be in place before
  or with them so that the grant added is `SELECT, INSERT` only.
- **`gip_app` cannot log in.** Measured on the shared container with the same query as above plus `rolcanlogin`:
  `gipricing|t`, `gip_app|f`. So the application cannot connect as `gip_app` as it stands; whether a new login role is made a
  member of `gip_app` (one grant set, the form the ruling's "a login role with `gip_app`'s grants" suggests) or `gip_app`
  itself gains `LOGIN`, and how the role is provisioned (`df53696a2682_platform_core_jobs_audit_events_outbox.py:72` creates it as
  `CREATE ROLE gip_app NOLOGIN`, so it is a group role by construction) is part of the DP.
- **Blast radius:** S-b touches every database path, so it lands after the current gate and NFR sessions and before the
  4 November freeze, with a full gate and a compose run (the ruling's schedule).

## The test that must hold

Red on `main` by cause: (i) an assertion run through the application's own connection that `current_user` is not the owner
of the artifact tables and `rolsuper` is false, which fails on `main` (`gipricing`, `t`); (ii) the application, connecting
by its production DSN path, cannot `ALTER TABLE … DISABLE TRIGGER` on an artifact table and cannot
`SET session_replication_role = replica`, each refused with `permission denied` or `must be owner/superuser`; (iii) per
legitimately written table, the application can still make its writes (the audited grants), each red-first when a grant is
removed. The migration path, run as the owner, is asserted separately so the two roles are not conflated.

*2026-10-14: per the maintainer's (by delegation) "2026-10-14 12:18:57 BST" (`to-lead.md`), item (2): "DP-14 (FD 8038 states the DISABLE TRIGGER dependency + a startup check): as recommended", and "NEW, from your 12:07:50 measurement (the owner `gipricing` is SUPERUSER, rolsuper = t): the app today can bypass ALL triggers via `session_replication_role`, not only DISABLE TRIGGER. S-b's startup refusal and test MUST assert the app's login role is NOT superuser, NOT the table owner, has NOBYPASSRLS, and cannot SET session_replication_role (a red: the SET attempted as the login role → refused). FD 8038's text states the superuser fact, measured by auditor-failauth with the query and output, and its HIGH stands."*

## Disposition

Carry forward, owner WK-1178: fixed in P2 (D17), by PL 8016's slice S-b, ruled at "2026-10-14 12:00:14 BST". FD-1728 (S-a)
is first and independent; FD-1704's revoke becomes meaningful only after this lands. It needs a resolution before any P3
start (`CLAUDE.md` §14). The event that next confirms or discharges it is the merge of S-b with the three reds above shown
on the base tree by cause.
