---
id: PL-8319
family: plan
kind: map
title: WK-674 — the frontend-image limb of FR-432 (FD-1661) and the roll cleanup's stopped container (FD-1816), one SOLO compose gate, the remaining SL-1689 row — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-05             # filed under working id 8319
owner: planner
tree: dae9637ea6f6a56f6502e9db70392cdfb2f3983d
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1688, PL-1237, SL-1689, SL-1968, SL-1813, FD-1661, FD-1816, FD-1970, FR-432, NFR-531]
---

# PL-8319 — WK-674: the frontend-image limb and FD-1816 (the SL-1689 row, a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"). It `relates:` `PL-1688` and leaves it unedited (a filed
> plan is frozen). It holds one row: the existing **SL-1689** (WK-674, `draft`), whose scope is
> narrowed here to FR-432's `frontend` limb and widened by FD-1816. The executor's skills are
> `superpowers:test-driven-development`, `.claude/skills/python-test`, `dev-commands`,
> `vue-frontend`, `repo-architecture`, `spec-change` (Task R4 only) and `git-hygiene`. The slice's
> ledger is LG 8320. PL 8319 and LG 8320 are working ids reserved by the lead.

## Authority

- **The user's decision and the order.** The maintainer's entry "2026-11-05 09:58:58 GMT" in
  `~/gi-pricing-plan.local/channel/to-lead.md`: "CODE FREEZE Thu 12 Nov"; "ALL 24
  FIX-BEFORE-FREEZE rows AND FD-1337 (7 h) AND FD-1484 (8 h) are coded and merged before Thu 12";
  "ORDER: WK-674's pair first (FD-1661 frontend limb + FD-1816, one SOLO compose gate — it unblocks
  WK-674's close)"; "a red gate = fix-and-regate within the chain, and only a slice still red at
  Wed 12:00 goes to the exception list".
- **The triage.** `~/gi-pricing-plan.local/handover/p2-code-owed-triage-2026-11-05.md`
  (`b28ba8e9454c`) §2, accepted as the proposal of record by the entry "2026-11-05 09:51:53 GMT".
- **PL-1688's three conditions stand** (the entry "2026-10-12 03:09:50 BST", DP-S4-3 (b)): a cut
  ladder moves the row by a dated line and never drops it; a new base image updates
  `docs/skills-map.md` in the same PR; the image is proved from a clean copy of the commit by a
  curl 200 on `/`, recorded in the LG.
- **The ruled port.** DP-B2 (a), `PL-1688`: `${GIP_WEB_PORT:-5173}`, with no realm change.
- **The limbs that already landed.** `api`, `migrate`, `worker-*`, `lb`: #1337 `eea416ca`.
  `scheduler`: #1409 `aad4fd58` (SL-1968). FD-1661's annotation of 2026-10-29 ends "**Status
  unchanged: the `frontend` limb remains, owner SL-1689 (WK-674).** FR-432 stays open until it
  merges."

## Goal

After this slice merges, `frontend` is a service under the `app` profile, its image builds from a
clean copy of the commit and serves the SPA with a history fallback and an `/api/` route to `lb`,
and a failed `api` roll leaves a stopped pre-roll container in place. FR-432's last limb, FD-1661
and FD-1816 close.

## Evidence at `dae9637e` (read, not run)

Every cite was read at `origin/main` `dae9637ea6f6a56f6502e9db70392cdfb2f3983d`, unless it names
the branch. No docker command was run by the planner.

**FD-1661, the frontend limb.**

- `git ls-tree -r --name-only origin/main deploy` has no `frontend.*` file, and
  `deploy/docker-compose.yml` has no `frontend:` service (`git grep -n frontend origin/main --
  deploy/docker-compose.yml` prints nothing).
- **The work is already authored and has never been run.** The branch
  `sl-1689-wk674-scheduler-frontend-image` (head `19c528e4`, a KEEP worktree, read only, merge base
  `f3462d8f`) carries `deploy/frontend.Dockerfile`, `deploy/frontend.Dockerfile.dockerignore`,
  `deploy/frontend.nginx.conf`, the frontend hunks of `c80009ad` and the docs hunks of `cac622f8`.
  Its ledger LG 8137 says the fresh-checkout proof was "owed to the build window", and no window
  ran. **So the first `docker build` of this Dockerfile is R3. It is a premise until then.**
- **The salvage is stale in one place.** The branch's `ports: ["${GIP_WEB_PORT:-5173}:80"]`
  publishes on every interface. #1378 (`8c3d3013`, "bind every published compose port to
  127.0.0.1", PL-1769 Step 1.5) came after it: every published port at `dae9637e` starts
  `127.0.0.1:` (`deploy/docker-compose.yml:39,54,69,95,194`). The ported hunk takes the same
  form, and the branch's shape check (`startswith("${GIP_WEB_PORT:-5173}:")`) changes with it.
- **The isolated overlay has no entry for `frontend`.** `deploy/docker-compose.isolated.yml` moves
  `postgres`, `redis`, `minio` to ephemeral ports "so a test project must not publish them". A
  test project that starts `frontend` would otherwise take host 5173. The overlay gains the entry.
- **The build is not `compose build`.** LG 8137's Task 0 reads buildx `0.13.1+ds1`; `PL-1688` row 2
  R1 (SL-1968) records that this is below the 0.17.0 `compose build` needs, so images are built
  with `docker build` and started with `up --no-build`. `_build_from_commit`
  (`backend/tests/deploy_stack_helpers.py:292-304`) already builds from `git archive <sha>` into a
  temporary directory; a clean copy by construction, and its form is reused for the frontend image.
- **The SPA needs no build-time environment.** `git grep -n 'import.meta.env' origin/main --
  frontend/src` prints no non-test line; the OIDC values come from the API at run time
  (`frontend/src/auth/config.ts:10-13`, `loadAuthConfig`, `request("/auth/config")`).
- **The demo's census is unaffected.** `compose_services` (`scripts/demo.py:296-302`) is a fixed
  set that does not name `frontend`, so `check_compose_up` does not start refusing.
  **But its hint changes meaning.** `check_compose_up`'s message (`:338-342`) tells the operator to
  run a bare `up -d --wait --scale api=2`, and after this slice a bare `up --profile app` also
  starts `frontend`, whose image a `docker build` of `deploy/Dockerfile` does not produce. DP-D2
  below.
- **The docs row is still absent.** `git grep -n -i nginx origin/main -- docs/skills-map.md
  docs/specs/07-platform.md` prints nothing, so `PL-1688` Task 4's second branch applies.
- **The roadmap row is stale.** `PL-1688` row 2 says "ONE dated line appended to SL-1689's roadmap
  row at SL-1968's mint". `git show origin/main:docs/roadmap.md | sed -n 1263,1282p` holds no such
  line: the row still reads as the scheduler and frontend. The dated line in A12 pays that debt.

**FD-1816.**

- `deploy/roll-api.sh:30-33` `api_ids` is `docker ps -q` (running only). `:36` `mapfile -t old <
  <(api_ids)`. `:41-55` `cleanup_new` removes `comm -13 <old> <(docker ps -aq …)`. `:56` the trap.
  The essay's cites hold.
- **The essay's fix has a second site, which it does not name.** `:59` scales to
  `$((REPLICAS * 2))` and `:61` derives `new` as `comm -13 old api_ids`. `up --scale` converges on
  the count of the service's containers, stopped ones included, and it starts stopped ones. Read
  from Compose's behaviour, **not run here**. If so, with two running and one stopped: Compose
  starts the stopped one and creates one new, so `-a` in `old` alone gives one `new`, and the roll
  fails at `:62` on a stack that would otherwise roll. Without the `-a`, today, the restarted old
  container counts as new, which is the path to the force removal. R0 reads this before R1 is
  written. DP-D1 turns on it.
- The neighbouring test, `test_a_failed_api_roll_leaves_the_pre_roll_replicas_and_no_never_healthy_one`
  (`backend/tests/test_deploy_stack_runtime.py:255`), and `_api_containers_all_states` (`:241`)
  give the form of the new test.

**The surrounding facts.**

- The CI that fires on `deploy/**` plus `backend/tests/**`: `python.yml`, `docs.yml`,
  `history-policy`. `frontend.yml` paths do not include `deploy/**`
  (`.github/workflows/frontend.yml:19-44`); the executor derives the set from the path filters by
  three-dot diff before polling.
- `git diff --name-only origin/main...origin/<b> -- deploy/` over every remote head at 10:02 UTC
  prints only `sl-1689-wk674-scheduler-frontend-image`. The serial rule on
  `deploy/docker-compose.yml` is free at the time of filing; R0 re-reads it.
- `df -h /` at 10:02 UTC: 6.7 GB free of 59 GB, 89% used. See "Needs".

## Decision points

For the maintainer, on the GO. Each is ruled before the slice starts.

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-D1 | What is FD-1816's fix (the essay: "the slice decides the detail")? | (a) **`old` becomes the `-a` listing and the scale-out target becomes `$(( ${#old[@]} + REPLICAS ))`.** One set, used by every site; stopped pre-roll containers are "old", the success path removes them, a failed roll leaves them. (b) Keep `old` running-only and add a second set `before` (`-a`), used by `cleanup_new` only. The roll path is byte-unchanged, and a restarted old container still counts as new. (c) `-a` on `old` only, as the essay's first sentence reads. (d) Exclude by creation time after the roll's start. | **(a)**, if R0 confirms the Compose reading. It is the one option where the success path is also right: (b) leaves the old image in `new`, so the roll fails the final image check at `:86` *after* the old replicas are gone, and (c) refuses every roll while a stopped replica exists. (d) depends on clock comparison, for no gain. If R0 refutes the reading (Compose leaves the stopped one stopped), (c) is enough and the executor reports before writing. |
| DP-D2 | The bare `up` in `check_compose_up`'s hint and the README now also start `frontend`, whose image is built separately (Evidence). What changes? | (a) **Docs only:** `deploy/README.md`'s build block gains the `docker build -f deploy/frontend.Dockerfile` line with the `GIP_BUILD` tag, and `demo.py` is unchanged. The stack the hint brings up is then the whole FR-432 stack. (b) Change the hint to name its services (`lb scheduler worker-*`), so the demo does not need the frontend image. | **(a).** FR-432's "working stack" includes `frontend`, and a hint that avoids it would hide the limb this slice adds. `scripts/` stays out of the write set. The cost: the SL-1913 rehearsal's stack bring-up builds one more image. Named in Hand-off. |

The rest of the design is closed by `PL-1688` (DP-B1, DP-B2, the nginx image, the context, the
conf) or by this delta's constraints.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's
merge tree. Items 1 and 2 apply to this plan; A1 to A13 apply to the slice. `PL-1688`'s Acceptance
items 3, 5, 6 and 7 are restated here for the `frontend` limb and read from here; its item 4 was
discharged by SL-1968.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no
   failing line except check 31 / check 32 lines naming the working ids 8319 and 8320. After the
   mint, `audit-docs.py` and `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints
   no line that stands for a set of ids.

The slice:

- **A1. The write set.** `git diff --name-only origin/main...HEAD` lists only the Write set below.
  Nothing under `frontend/`, `backend/src/`, `packages/` or `scripts/`.
- **A2. Red first, by cause, for each finding, on the slice's named base.** The LG quotes: `no
  service named frontend`, `frontend.nginx.conf does not exist`, the port check's own line, and
  FD-1816's assert with the removed container's id (R1, R3). `KeyError`, a fixture or a build error
  is not the red.
- **A3. Shape green.** `uv run pytest -q backend/tests/test_deploy_stack.py -k frontend` exits 0
  and collects at least 4 tests, and the breaker table carries three frontend rows, each seen to go
  red on its break (`test_each_check_goes_red_on_the_break_it_exists_for`).
- **A4. The declared services.** `docker compose -f deploy/docker-compose.yml --profile app config
  --services | sort` prints `api`, `frontend`, `lb`, `migrate`, `scheduler` and the four
  `worker-*` beside the dependencies. `docker compose -f deploy/docker-compose.yml config
  --services` (no profile) is unchanged from the base, three services.
- **A5. Reachable from the commit** (`PL-1688` Acceptance 5). In the build window, under
  `GIP_DEPLOY_TESTS=1`, the new runtime test (R2) passes on an image built from `git archive <sha>`:
  `/` → `200` with `text/html`; a deep SPA route → `200` (the history fallback); one `/api/v1/…`
  route → the API's own status with an RFC 9457 body, never nginx's `502`. The LG quotes the
  three statuses with the `<sha>`.
- **A6. FD-1816.** Under `GIP_DEPLOY_TESTS=1` the new test (R3) is seen red at the base and green
  at the head: a stopped pre-roll `api` container is present after a failed roll.
- **A7. No regression of the roll.** Under `GIP_DEPLOY_TESTS=1`, the full
  `backend/tests/test_deploy_stack_runtime.py` passes at the head, naming
  `test_previous_version_serves_the_migrated_schema_and_rolls_forward_with_no_failures` (NFR-531)
  and the failed-roll test in the quoted summary.
- **A8. The tech dependency, same PR.** `git grep -n -i nginx -- docs/skills-map.md
  docs/specs/07-platform.md` prints the two new rows, and `git diff origin/main...HEAD --
  docs/specs/07-platform.md` touches §8 only and no requirement id. `audit-docs.py` rc 0 at the
  minted head.
- **A9. The shared stack.** Before and after the window the LG quotes `docker ps --format
  '{{.Names}} {{.Status}}' | grep gi-pricing-`, unchanged in container set, with keycloak's bind
  source under tools-main (common seat brief, items 20 and 24). Nothing ran against project
  `gi-pricing`. The window's own cleanup quotes `docker ps -a --filter
  label=com.docker.compose.project=gip-s4-runtime -q | wc -l` = 0.
- **A10. The GREEN set** is derived by import closure (common seat brief, item 29), starting from
  LG 8137's derivation and re-derived at the re-merged head; the LG quotes commands and list.
  Expected: `test_deploy_stack.py`, `test_deploy_stack_runtime.py`, `test_deploy_switch_runtime.py`.
- **A11. The full code gate, both halves, SOLO, compose-changing**, green at the re-merged head,
  every rc quoted, with the template's shared-stack restore rows from tools-main. The frontend half
  covers `pnpm --dir frontend build` on the same tree. A pre-existing red is not excused here: it
  is reported and the lead rules.
- **A12. FD closing acts, in the FD-1842 form, in the slice's own PR, by the slice's auditor.**
  For each of FD-1661 and FD-1816: the essay's `status: closed`, `relates:` gaining the slice's
  ids, a `***Resolved <date>***` paragraph naming the delivered remedy, its red and its LG, the
  same line on the register row, and the PR number and squash added at the merge's date of record.
  The SL-1689 row gains one dated line recording that SL-1968 took the `scheduler` limb, that
  SL-1689's scope is the `frontend` limb plus FD-1816 under this delta, and FD-1816's addition to
  its `relates:`. `FR-432` is met at this merge; the auditor reads the requirement's whole text
  including "seeded demo data (R2)" and says what evidences it (SL-1711's compose journey is the
  expected citation), rather than taking it from this plan.
- **A13. The LG Audit section**, with the lead's adoption, lands in the audit's own commit, and
  `docs/INDEX.md` is regenerated after the closing acts (common seat brief, item 17).

## Global Constraints

- **B1. Port the named hunks; never merge the old branch.** As `PL-1688` row 2 R0: the executor
  ports onto a branch from this plan's draft branch. It does not merge, rebase or move
  `sl-1689-wk674-scheduler-frontend-image`, and it does not write its worktree (KEEP list). The LG
  lists each hunk with its source commit. LG 8137 is cited by branch and path, and is not carried.
- **B2. Serial on `deploy/docker-compose.yml`** (the entry "2026-10-12 02:53:52 BST"). R0 repeats
  the census over every remote head and names any branch touching `deploy/`.
- **B3. `deploy/**` carries one gate.** "One SOLO compose gate": FD-1816 is not split out.
- **B4. The frontend publishes on loopback**, like every other port since #1378.
- **B5. No hand-written API type** (`CLAUDE.md` §3). The image runs `generate:api` from the
  committed `docs/contracts/openapi/generated.json`; nothing generated is copied in.
- **B6. The realm is not edited** (DP-B2 (a)). The backend image's root `.dockerignore` is not
  widened.
- **B7. `lb.conf` and the `api`, `worker-*`, `migrate`, `scheduler` services are unchanged.**
- **B8. Red first, by cause. No test is removed or weakened** (common seat brief, item 13).
- **B9. If the frontend image build fails on a cause that needs `frontend/`, `backend/src/` or
  `scripts/`, STOP and report.** Those are outside the write set.

## Needs

- **DB / Redis.** The slice uses **no shared database and no shared Redis**: no `createdb`, no
  `redis-cli`, no template, no `GIP_REDIS_URL`. The runtime tests run on the throwaway project
  `gip-s4-runtime`, with its own postgres and redis containers on ephemeral ports, torn down by
  `down`. The shared db 0 is live and is never touched. The gate uses its own slot's dbs.
- **A build window, lead-granted in writing**, single-tenant, outside any gate and any timed stage;
  load1 and `free -g` read at start and quoted (common seat brief, item 15). Compose runtime tests
  are never small runs (item 32). About 1.5 h: two app images (N and N-1) and one frontend image.
- **Disk.** The window reads `df -h /` and `docker system df` first. **Planner's floor, unmeasured:
  stop under 5 GB free.** The frontend build's `node:22-alpine` stage and `pnpm install` are new
  weight, and the box is at 6.7 GB. Any prune is the user's word and never the seat's (item 35).
  Removal of the window's own images is by exact tag (`docker image rm
  gi-pricing-frontend:<sha>`) and its output is quoted.
- **Network** for `node:22-alpine` and the pnpm store inside the build.
- **NFR VM:** nothing.

## Tasks

### SL-1689 — the frontend image and service; FD-1816

**The row.** First in the 09:58:58 order. Existing row, WK-674, `draft`. Lane: one `sonnet`
executor (the executor charter's model line governs).

- **Scope (what LG 8320 quotes):** R0 to R4 and G below.
- **Requirements:** `07` §3.2 FR-432 (the `frontend` limb), NFR-531 (read: the roll is unchanged on
  its success path).
- **Register:** FD-1661 (MEDIUM), FD-1816 (LOW), owner WK-674, close at the merge (A12).
- **Depends on:** DP-D1 and DP-D2 ruled; the maintainer's GO; the build window; the gate slot.
- **Size:** 5 h of seat time (triage: 7 h; the Dockerfile, conf and shape checks exist), with the
  1.5 h window inside it. SOLO gate about 2.5 h, not counted.
- **Calendar:** merged before Thu 12 Nov 2026; a slice still red at Wed 11 Nov 12:00 goes to the
  exception list (09:58:58). `PL-1688` B0.3's cut-ladder line stands.

**R0 — premises, no write.** At the slice's base:

1. Repeat B2's census and quote it.
2. Re-read every Evidence line that names a line number. A moved line is noted in the LG; a
   changed fact stops the slice.
3. Read Compose's behaviour for FD-1816 on a throwaway project in the build window, before R1's
   FD-1816 test is written: `up --scale api=3`, `docker stop` one of the three; `up -d --no-deps --no-recreate --scale api=4 api`; quote `docker ps -a`
   for the service. This settles DP-D1's branch. **If it differs from the Evidence, report before
   writing the fix.**

**R1 — the shape tests, red first, no Docker.**

In `backend/tests/test_deploy_stack.py`, ported from `c80009ad` (`:211-262`, `:378-390`, `:473-478`,
`:504-505` of the branch), each marked `req("FR-432")`:

- `frontend_is_built_from_its_dockerfile`, with the port line changed (B4):

  ```python
  ports = [str(p) for p in frontend.get("ports") or []]
  if not any(p.startswith("127.0.0.1:${GIP_WEB_PORT:-5173}:") for p in ports):
      problems.append("frontend does not publish ${GIP_WEB_PORT:-5173} on 127.0.0.1")
  ```

- `nginx_conf_problems`, `frontend_proxies_api_to_lb` and
  `backend_image_context_still_excludes_the_frontend` as authored, and the three `test_the_frontend_…` /
  `test_the_backend_image_context_…` tests. The last is a guard, green at base and head, and is
  recorded as a guard.
- **The breaker table** gains `_break_frontend_missing`, `_break_frontend_other_dockerfile` and,
  new:

  ```python
  def _break_frontend_on_every_interface(c: dict[str, Any]) -> None:
      c["services"]["frontend"]["ports"] = ["${GIP_WEB_PORT:-5173}:80"]
  ```

**The red, by cause:** `no service named frontend` and `frontend.nginx.conf does not exist` at the
base. The breaker rows go red by `KeyError` at the base, which is not a red by cause: they are added
after the compose edit and proved by their own run (LG-1969's note on `c80009ad`'s breakers). Run
through `~/gi-pricing-plan.local/handover/run-small.sh`, one file.

**R1 green.** Port from the branch unchanged: `deploy/frontend.Dockerfile`,
`deploy/frontend.Dockerfile.dockerignore`, `deploy/frontend.nginx.conf`. Add to
`deploy/docker-compose.yml`, after `scheduler`, the `c80009ad` block with the comment re-read
against B4 and:

```yaml
    ports: ["127.0.0.1:${GIP_WEB_PORT:-5173}:80"]
```

Add to `deploy/docker-compose.isolated.yml`:

```yaml
  frontend:
    ports: !override ["127.0.0.1::80"]
```

**R2 — reachable from the commit (build window; A4, A5).**

- `backend/tests/deploy_stack_helpers.py` gains `_build_frontend_from_commit(sha)`, the
  `_build_from_commit` form: `git archive <sha>` into a temporary directory, then `docker build -f
  deploy/frontend.Dockerfile -t gi-pricing-frontend:<sha> .` there. Share the archive step between
  the two rather than copying it.
- `backend/tests/test_deploy_stack_runtime.py` gains, marked `req("FR-432")` and behind the file's
  existing `GIP_DEPLOY_TESTS` skip, on the `down` fixture:

  ```python
  def test_the_frontend_serves_the_spa_and_reaches_the_api_through_lb(built_n: str, down: None) -> None:
      _build_frontend_from_commit(built_n)
      _compose(built_n, "up", "-d", "--no-build", "--wait", "frontend")
      port = _compose(built_n, "port", "frontend", "80").stdout.strip().rsplit(":", 1)[-1]
      # `/` 200 text/html; a deep SPA route 200; `/api/v1/auth/config` answers from the API
      ...
  ```

  The elided body is three `urllib.request` reads using `port`. It asserts the three statuses in
  A5, picks the deep route from `frontend/src/router` at Task time, and asserts the third response
  is not nginx's: a JSON body from the API. Its name uses `_compose`, so login-role provisioning
  (FD-1970) comes with it, and no hand-run stack is needed.
- `PL-1688`'s Acceptance 5 says `git worktree add` or a clone; **`git archive <sha>` replaces it
  here** because the helper's form is a clean copy of the commit and leaves no worktree behind.
  This is a stated change, not a drift.
- **First-build reds are expected to be possible.** If `vue-tsc --build` reads a file outside the
  ignore file's admit list, fix the ignore file (it is in the write set), quote the error in the
  LG, and rebuild. B9 governs a fix outside the write set.

**R3 — FD-1816, red first (build window; A6, A7).**

`backend/tests/test_deploy_stack_runtime.py`, marked `req("NFR-531")`, beside `:255`, same
never-healthy overlay as that test:

```python
def test_a_failed_api_roll_leaves_a_stopped_pre_roll_container(
    shas: tuple[str, str], down: None, tmp_path: pathlib.Path
) -> None:
    """FD-1816: a stopped pre-roll container is not the roll's to remove."""
    n1, n = shas
    _compose(n1, "up", "-d", "--wait", "--scale", "api=3", "lb")
    running = sorted(_api_containers())
    stopped = running[-1]
    subprocess.run(["docker", "stop", stopped], check=True, capture_output=True)
    before = sorted(_api_containers_all_states())
    # the never-healthy overlay and the roll call, exactly as in :268-286
    assert result.returncode != 0, "the roll must fail when no new replica turns healthy"
    remaining = sorted(_api_containers_all_states())
    assert stopped in remaining, f"cleanup removed the stopped pre-roll container {stopped}"
    assert remaining == before
```

**The red, by cause:** at the base, `cleanup removed the stopped pre-roll container <id>`, with
`roll-api` printing `cleanup: removed new <id>`. **R3 green:** DP-D1 as ruled. Under (a), in
`deploy/roll-api.sh`: `old` is built from `docker ps -aq` with the same two filters; the scale-out
target is `$(( ${#old[@]} + REPLICAS ))`; the say line at `:58` follows it; the header comment (`:2-12`)
says what a stopped pre-roll container does. Nothing else changes: `api_ids` keeps `-q`, because
`new` and `final` mean running. **Then A7**: the whole runtime file, `GIP_N_SHA` and `GIP_N1_SHA`
set. The window's end: A9's three reads.

**R4 — the docs, same PR.** `spec-change` for the `07` §8 edit. Port `cac622f8`'s `docs/skills-map.md`
rows and `07` §8 rows, and only the `frontend` bullet of `deploy/README.md` (SL-1968 took the
scheduler line), re-reading B4 into its text ("publishes `127.0.0.1:${GIP_WEB_PORT:-5173}`"). DP-D2
(a): the README's build block (`:121-125`) gains the frontend `docker build` line and a line naming
the buildx limit. `roll-api.sh`'s behaviour with a stopped replica joins the README's roll bullet
(`:129-131`). `python3 scripts/audit-docs.py` through `run-heavy.sh --light` before commit.

**G — the gate.** The full code gate, both halves, SOLO on gate-1: this is a compose-changing diff,
so **not pairable** (the template's criterion (e), `deploy/docker-compose.yml` differs from main).
The shared stack is restored **only from tools-main** (the template's standing line and common seat
brief, item 20), with every row printed. Re-merge `origin/main` first, then the GREEN set, then the
gate. **Shared-fixture risk:** `deploy_stack_helpers.py` is imported by two runtime files and
`scripts/bench-deploy-path.py`; all skip without `GIP_DEPLOY_TESTS`, so the window (A7) is their
real cover, not the gate. No contract regeneration, no migration. CI expected: `python`, `docs`,
`history-policy`.

### Write set

- `deploy/docker-compose.yml` (the `frontend` service), `deploy/docker-compose.isolated.yml` (its
  overlay entry), `deploy/frontend.Dockerfile`, `deploy/frontend.Dockerfile.dockerignore`,
  `deploy/frontend.nginx.conf`, `deploy/roll-api.sh`, `deploy/README.md`.
- `backend/tests/test_deploy_stack.py`, `backend/tests/test_deploy_stack_runtime.py`,
  `backend/tests/deploy_stack_helpers.py`.
- `docs/skills-map.md`, `docs/specs/07-platform.md` (§8 only).
- LG 8320 under `docs/ledgers/`.
- At the mint: `docs/roadmap.md` (the SL-1689 row's status and A12's dated line), `docs/INDEX.md`,
  this plan's `status:`, the FD-1661 and FD-1816 essays and `docs/findings/register.md` (A12).

### Files shared with other groups

`docs/specs/07-platform.md` §8: shared only if A's or H's spec text lands in the same file, in
another section, and it merges textually. `backend/tests/` deploy files: no other group. **Safe
beside every group until the build window.** The window and the gate are serial with everything.

## Hand-off (not this plan's writes)

- DP-D1 and DP-D2 and the GO: the maintainer. The window grant and gate slot: the lead.
- The SL-1689 mint, LG 8320's id and the row's status: the lead; the LG: the executor; A12's
  closing acts and A13's audit: the slice's auditor; the adoption line: the lead.
- **For SL-1913's owner:** after this merges, a compose stack from the bare `up` needs
  `gi-pricing-frontend:$GIP_BUILD` built first (DP-D2 (a)).
- **The `sl-1689` worktree and branch** stay on the KEEP list until this merges. Their retirement
  is the lead's to ask of the user. Not a prune.
- FD-1836, FD-1508 and FD-1693 stay outside this slice (triage §2): WK-674's close needs them.
- `PL-1688` is not edited.

## Self-review

1. **Every cite was read** at `dae9637e`, or at the named branch commit. The Compose behaviour in
   FD-1816's Evidence is the one line not read from a file or run, says so, and R0 reads it first.
2. **Requirements by id:** FR-432, NFR-531. No range.
3. **Placeholders:** R2's and R3's elided lines name the exact lines or facts that fill them.
4. **Each red is by cause**, and a finding has its own: R1 for FD-1661 (R2 is reachability, no red
   available before the image), R3 for FD-1816.
5. **The triage is corrected in three places:** the frontend work is authored, not new (hence 5 h
   against 7 h); the salvaged port line is stale since #1378; and FD-1816's fix has a second site.
6. **Calendar weekdays** read with `date -d`: 12 Nov 2026 is a Thursday.
