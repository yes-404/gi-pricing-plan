---
id: FD-8094
family: finding
title: The FD-1684 media-type sweep predicate keys on an empty response schema, so a wrong media type on a typed schema trips nothing
status: active
created: 2026-10-17
owner: auditor
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
corrected_by: []
relates: [WK-1178, SL-1709, PL-1708, FD-1684]
---

# FD-8094 — The FD-1684 media-type sweep predicate keys on an empty response schema, so a wrong media type on a typed schema trips nothing

## Finding

**LOW; owner WK-1178; verdict deferred with an owner** (the maintainer, about 19:16 BST on
2026-10-17, the reservation recorded in `eta.md` at 19:15:42 BST). The sweep predicate of
FD-1684's Evidence section, used by PL-1708 AC 4 and by SL-1709, selects a 2xx response
media type only when its schema is exactly `{}`. A response that publishes a wrong media type
with a typed (non-empty) schema is not selected, so the predicate cannot detect that case.

## Evidence

The predicate, verbatim from the SL-1709 ledger (branch
`origin/sl-1709-wk1178-fd1684-prep-2026-10-16`, head `bcda8a28`, file
`docs/ledgers/LG-01775-wk-1178-slice-sl-1709-fd-1684-the-four-non-json-routes-declare-their-media-types-slice-ledger.md`,
audit finding F2):

`python3 -c "import json;d=json.load(open(<file>));[print(m.upper(),p,k,media) for p,i in d['paths'].items() for m,op in i.items() if isinstance(op,dict) and 'responses' in op for k,v in op['responses'].items() if k.startswith('2') for media,s in v.get('content',{}).items() if s.get('schema')=={}]"`

Re-read by this author: the only filter on the media type is the last clause,
`if s.get('schema')=={}`. It prints a line for a 2xx media type if and only if that media
type's schema is the empty object. A media type with `{"type":"string"}` or a `$ref` is never
printed, whatever its media type. The ledger's planted red confirms the limit: a wrong
`application/json` on `GET /api/v1/audit/export` printed only because the plant carried `{}`;
the ledger notes that "a media-type rename alone with a typed schema would not trip it".

## Disposition

Deferred with an owner: WK-1178. A later slice, or the next audit that reuses the predicate,
replaces it with one that compares each 2xx media type to the route's declared wire type, or
adds a contract test for that comparison. Until then, the predicate proves only the
empty-schema form of FD-1684. The event that next discharges it: a merged slice that changes
the predicate or adds that test.
