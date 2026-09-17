<!--
TEMPLATE — Phase (`P<n>`), a milestone label — outside the id standard, on principle
(§1.1 rule 4): it is cited as a placement (`phase: P2`), never as a document, and never
takes a number from `python3 scripts/doc-id.py next`. `<n>` is its own small,
incrementing sequence (`P0`, `P1`, `P2`; no letters from now on). Copy the section below
into docs/roadmap.md, replace `<n>` and the field values, fill in every placeholder, and
delete this comment.

This is the one section §1 defines that is *not* built from the closed header field set
of §1.5 — a phase section is plain fields under a heading, exactly as shown below, not
YAML front matter and not a document with an `id:`. Field spelling matches RFC-937 §1.3's
own illustration verbatim ("exit criteria", two words, not `exit_criteria`).
-->

## P<n> — <Title>
status: draft            # draft → active → closed (§1.2a)
opened: YYYY-MM-DD
target: YYYY-MM-DD
gates: plan freeze YYYY-MM-DD · code freeze YYYY-MM-DD · docs freeze YYYY-MM-DD
exit criteria: <what must be true, named by id where possible — e.g. "WF-NNNNN delivered
  end to end; no open FD- against <MODULE>">
works: WK-NNNNN, WK-NNNNN

<One paragraph of framing prose for the phase, if wanted — the fields above are what
`doc-index.py`'s phase report and `phase-close.md` read; this paragraph is not parsed.>
