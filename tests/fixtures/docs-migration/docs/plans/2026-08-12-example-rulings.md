# Example rulings, filed together (2026-08-12)

A worked example of the legacy multi-ruling file shape: several `## Ruling N` sections in
one file, which the migration script splits one-per-ruling. This preamble line is the
only content before the first `## Ruling` heading, and is carried forward as part of the
first split ruling's own body — the concatenation of every split output reproduces this
file's body lines in order.

## Ruling 1 — Example decision A

### Question

A worked question, standing in for a real decision point.

### Ruling

Chosen for illustration. Cites `W1-1` for a slice this ruling applies to.

## Ruling 2 — Example decision B

### Question

A second worked question.

### Ruling

Also chosen for illustration only, so the migration script has more than one record to
split out of this one file.
