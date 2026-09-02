<!--
TEMPLATE — Workflow (`WF-`), a cross-module domain journey (CLAUDE.md §4).
Copy this file to `docs/workflows/WF-<nnnnn>-<slug>.md`, where `<nnnnn>` is the padded
result of `python3 scripts/doc-id.py next` — never chosen by hand. Fill in every
placeholder below, delete this comment block, and remove any field this workflow does
not use (the closed field set still applies — do not add one).

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6. This template shows only the fields
the Workflow family uses; `kind:`, `phase:`, `work:`, `slice:` and `plans:` do not apply
to this family and must not appear here.
-->

---
id: WF-NNNNN
family: workflow
title: <one line — the journey this describes, e.g. "Dataset to model">
status: draft                 # draft → active → superseded | retired (§1.2a)
created: YYYY-MM-DD
owner: decision-maker          # creates via spec-change; a filename under .claude/roles/, or `maintainer`
tree: <commit-sha this was written against>
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                    # ids only — the Works that deliver this journey's steps
---

# WF-NNNNN — <Title>

## Purpose

<What crosses module boundaries here, and why it is a journey rather than one module's
own spec section.>

## Steps

1. <Module> — <endpoint or pricing-core function, cited so FR-OVR-17 / OQ-OVR-6 can
   check it against that module's own §5.1 / §5.2>.
2. ...

## Coverage

<Which test owns `test_wfNN_journey` for this workflow (§1.6: "executor delivers and
owns `test_wfNN_journey`"), and what module spec sections it exercises (check 14's
coverage floor).>
