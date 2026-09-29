---
id: FD-9025
family: finding
title: The merge of #888 had no MERGE-ACK, and its squash subject names four working ids for seven minted ones
status: active
created: 2026-09-29
owner: auditor
tree: bb2aa935dbdf207a7073df85f8fde143e1cee77b
corrected_by: []
relates: [FD-1214, FD-1215, FD-1216, FD-1217, FD-1218, FD-1219, FD-1220, WK-1178]
---

# FD-9025 — The merge of #888 had no MERGE-ACK, and its squash subject names four working ids for seven minted ones

## Finding

**Severity: medium.** Filed under a **working id** (`FD-9025`); the lead mints it at its turn in the queue.

## Evidence

**What merged, and when.** `git show -s --format=%aI%n%cI bb2aa935` prints `2026-09-29T09:54:59+01:00` on both lines, and
`--format=%an|%cn` prints `yes 404|GitHub`: PR #888 was squash-merged as `bb2aa935` at 09:54:59 BST by the GitHub web-flow
committer. The deputy's entry "2026-09-29 09:59:24 BST · deputy · STOP: #888 was MERGED WITHOUT MY ACK; the id collision with
S3; no merge without a deputy ACK entry" (`to-lead.md`) records that no MERGE-ACK entry naming the SHA exists, which breaks the
standing rule that every merge needs one. This record read that entry; it did not search for an ACK itself.

**The squash subject cannot be changed and is wrong.** It reads: *"docs(findings): FD-[9018] to FD-[9021] (working ids); close
FD-1207 on #873; FD-1195 records FR-178 in two parts (#888)"*. Read against the change set
(`git diff --stat 633c6f34 bb2aa935`, 13 files), it is wrong twice:

1. **Ids.** The commit adds **seven** findings, `FD-1214` to `FD-1220`, minted ids, and no file or register row carries a
   working id. Commit `841f38a9` inside the PR renumbered the working ids 9018 to 9024 (the four-digit 90xx range) (mapping 9018→1214, 9019→1215, 9020→1216,
   9021→1217, 9022→1218, 9023→1219, 9024→1220). The subject names four ids, in the old form.
2. **Scope.** The PR also closes FD-1206 and FD-1207 (#883 and #873) and amends FD-1195 and FD-1210, which the subject mentions only in part; the body is the
   list of working-id commit titles, ending "Updated findings register, INDEX, and essay files with new ids."

**The correction.** For that commit, cite **FD-1214 to FD-1220**, never the working-id form. Anyone who searches the log for
the old id 9018 finds a commit whose files hold no such id.

**A second defect in the same PR**, corrected by the PR that files this record: `FD-1214` carried a paragraph, "Amendment —
2026-09-29, 09:49 BST", added inside `841f38a9`, that said more than the deputy's entry of 09:48:51 BST it rests on (a stop, a
re-lockdown, "WK-1178 is building test-infra"). It is replaced by a paragraph that states the entry's facts only.

**What the audit found clean at `bb2aa935`:** the rename (no old id remains; `id:`, filename and heading agree on all seven), the
register rows, the `created:` dates against the working-id drafts (`1de2eec7`), and `audit-docs.py`, `doc-id.py check`,
`doc-index.py --check` and `register-lint.py` all exit 0.

## Disposition

**Deferred with an owner — the lead.** The lead's standing rule is that only the lead merges, with a MERGE-ACK entry naming the
full SHA. Event: the maintainer accepts or rules on the unapproved merge. Which rule or check could have stopped it (the merge
was made by a teammate's account) is a question in no charter, so it is the lead's.
