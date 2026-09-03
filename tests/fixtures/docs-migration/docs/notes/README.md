# Working notes

Notes from the maintainer: requests, standing intentions, and the assessment each one got
before work started. **One file per topic**, the same convention as
[`docs/adr/`](../adr/README.md), for the same reason.

```bash
# Next number. Same command as adr-write, pointed at this directory.
ls docs/notes/ | grep -oE '^[0-9]{4}' | sort -n | tail -1
```

## Index

| Note | Title | Raised | Status |
|---|---|---|---|
| [NT-0001](0001-example-note.md) | An example note for the migration fixture | 2026-08-11 | `landed` |

## What a note must contain

A header block of exactly these fields, then the body.

## The audit standard

**Seven checks. Each note, every time** — the ⚙ ones are enforced by the script, and the
rest are yours:

7. ⚙ **The index above matches the files.** Check 18, both directions: every note listed,
   every listed row backed by a file, and the number, link target and status agreeing in
   both places.

That is the whole of the mechanical half.
