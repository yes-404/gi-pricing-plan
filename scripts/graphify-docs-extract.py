"""Deterministic semantic extraction over docs/*.md for graphify.

The spec suite's structure is explicit text — requirement ids, ADR references,
open questions and section citations are literally written down — so parsing
beats asking a model to guess at them. Every edge this emits is EXTRACTED at
confidence 1.0 because it corresponds to a citation that is really in the file.

Node ids follow graphify's rule exactly: full repo-relative path, extension
dropped, every segment lowercased with non-alphanumerics collapsed to `_`,
joined with `_`, then `_` + normalised entity name.
"""

from __future__ import annotations

import ast as pyast
import json
import re
import sys
from pathlib import Path

DOCS = Path("docs")
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "graphify-out/.graphify_semantic.json")


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def stem_id(path: Path) -> str:
    parts = list(path.parts)
    parts[-1] = path.stem
    return "_".join(norm(p) for p in parts)


REQ_DEF = re.compile(r"^\|\s*\*\*((?:FR|NFR)-[A-Z]+-\d+)\*\*\s*\|\s*(.*?)\s*\|?\s*$")
REQ_REF = re.compile(r"\b((?:FR|NFR)-[A-Z]+-\d+)\b")
ADR_REF = re.compile(r"\bADR-(\d{4})\b")
OQ_REF = re.compile(r"\b(OQ-[A-Z]+-\d+)\b")
# A decided question is struck through and ticked — `| ~~**OQ-DATA-7**~~ ✔ |` — so the
# leading `~~` and any trailing marker are optional, not part of the id.
OQ_DEF = re.compile(r"^\|\s*~{0,2}\*\*(OQ-[A-Z]+-\d+)\*\*~{0,2}\s*[^|]*\|\s*(.*?)\s*\|?\s*$")
SPEC_REF = re.compile(r"`(\d{2}-[a-z-]+)\.md`")
WF_REF = re.compile(r"\b(wf-0[1-5])\b")

nodes: dict[str, dict] = {}
edges: list[dict] = []
hyperedges: list[dict] = []

files = sorted(p for p in DOCS.rglob("*.md"))

# Where each identifier is DEFINED, so a citation points at the definition
# rather than manufacturing a duplicate node per citing file.
req_home: dict[str, str] = {}
oq_home: dict[str, str] = {}
adr_home: dict[str, str] = {}
spec_home: dict[str, str] = {}
wf_home: dict[str, str] = {}


def add_node(
    nid: str,
    label: str,
    file_type: str,
    source_file: str,
    source_location: str | None = None,
    rationale: str | None = None,
) -> str:
    if nid in nodes:
        if rationale and not nodes[nid].get("rationale"):
            nodes[nid]["rationale"] = rationale
        return nid
    n = {
        "id": nid,
        "label": label,
        "file_type": file_type,
        "source_file": source_file,
        "source_location": source_location,
        "source_url": None,
        "captured_at": None,
        "author": None,
        "contributor": None,
    }
    if rationale:
        n["rationale"] = rationale
    nodes[nid] = n
    return nid


def add_edge(
    src: str,
    tgt: str,
    relation: str,
    confidence: str = "EXTRACTED",
    score: float = 1.0,
    source_file: str | None = None,
    loc: str | None = None,
) -> None:
    if src == tgt or src not in nodes or tgt not in nodes:
        return
    edges.append({
        "source": src,
        "target": tgt,
        "relation": relation,
        "confidence": confidence,
        "confidence_score": score,
        "source_file": source_file,
        "source_location": loc,
        "weight": 1.0,
    })


# ---------------------------------------------------------------- pass 1: define
for path in files:
    rel = path.as_posix()
    sid = stem_id(path)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title = path.stem
    for line in lines[:20]:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    add_node(sid, title, "document", rel, "L1")

    # A spec document is citable as `NN-name.md`.
    m = re.match(r"^(\d{2}-[a-z-]+)$", path.stem)
    if m:
        spec_home[m.group(1)] = sid

    m = re.match(r"^(wf-0[1-5])", path.stem)
    if m:
        wf_home[m.group(1)] = sid

    # An ADR *is* its document — a separate concept node beside it would be the same
    # decision counted twice, and citations would split across the pair.
    m = re.match(r"^(\d{4})-", path.stem)
    if m and "adr" in path.parts:
        adr_home[m.group(1)] = sid

    for i, line in enumerate(lines, start=1):
        rm = REQ_DEF.match(line)
        if rm:
            rid, body = rm.group(1), rm.group(2)
            nid = f"{sid}_{norm(rid)}"
            add_node(nid, rid, "concept", rel, f"L{i}", rationale=body[:500])
            req_home.setdefault(rid, nid)
            add_edge(sid, nid, "references", source_file=rel, loc=f"L{i}")

        # `open-questions.md` is the register; a spec's §10 mirrors the same question,
        # so only the register defines it and every mirror becomes a citation of it.
        om = OQ_DEF.match(line) if path.name == "open-questions.md" else None
        if om:
            oid = om.group(1)
            body = (om.group(2) or "").strip()
            if oid:
                nid = f"{sid}_{norm(oid)}"
                add_node(nid, oid, "concept", rel, f"L{i}", rationale=body[:400])
                oq_home.setdefault(oid, nid)
                add_edge(sid, nid, "references", source_file=rel, loc=f"L{i}")

# ---------------------------------------------------------------- pass 2: cite
for path in files:
    rel = path.as_posix()
    sid = stem_id(path)
    lines = path.read_text(encoding="utf-8").splitlines()

    for i, line in enumerate(lines, start=1):
        rm = REQ_DEF.match(line)
        owner = f"{sid}_{norm(rm.group(1))}" if rm else sid
        body = rm.group(2) if rm else line

        for rid in REQ_REF.findall(body):
            tgt = req_home.get(rid)
            if tgt:
                add_edge(owner, tgt, "references", source_file=rel, loc=f"L{i}")

        for num in ADR_REF.findall(body):
            tgt = adr_home.get(num)
            if tgt:
                add_edge(owner, tgt, "cites", source_file=rel, loc=f"L{i}")

        for oid in OQ_REF.findall(body):
            tgt = oq_home.get(oid)
            if tgt:
                add_edge(owner, tgt, "references", source_file=rel, loc=f"L{i}")

        for spec in SPEC_REF.findall(body):
            tgt = spec_home.get(spec)
            if tgt:
                add_edge(owner, tgt, "references", source_file=rel, loc=f"L{i}")

        for wf in WF_REF.findall(body):
            tgt = wf_home.get(wf)
            if tgt:
                add_edge(owner, tgt, "references", source_file=rel, loc=f"L{i}")

# ------------------------------------------------- pass 3: requirement -> evidence
# `@pytest.mark.req("FR-DATA-16")` is this repo's traceability spine (CLAUDE.md §13).
# It is an explicit, machine-checked citation of a requirement id from inside code, so
# the edge is EXTRACTED — the one link that turns the spec half of this graph and the
# code half into a single traversable object.
marker_edges = 0
unknown_reqs: set[str] = set()
# `examples/` carries markers too — the freMTPL2 seed evidences FR-PLAT-37, and leaving
# the directory out silently lost that one edge (caught by diffing against req-coverage.py).
code_roots = [Path("backend"), Path("packages"), Path("tests"), Path("scripts"), Path("examples")]

for root in code_roots:
    if not root.exists():
        continue
    for py in sorted(root.rglob("*.py")):
        if ".venv" in py.parts:
            continue
        try:
            tree = pyast.parse(py.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        sid = stem_id(py)
        rel = py.as_posix()
        for node in pyast.walk(tree):
            if not isinstance(node, (pyast.FunctionDef, pyast.AsyncFunctionDef, pyast.ClassDef)):
                continue
            for dec in node.decorator_list:
                if not isinstance(dec, pyast.Call):
                    continue
                name = pyast.unparse(dec.func)
                if not name.endswith("mark.req"):
                    continue
                for arg in dec.args:
                    if not isinstance(arg, pyast.Constant) or not isinstance(arg.value, str):
                        continue
                    rid = arg.value
                    tgt = req_home.get(rid)
                    if not tgt:
                        unknown_reqs.add(rid)
                        continue
                    src = f"{sid}_{norm(node.name)}"
                    # The test node comes from the AST pass; declare it only if that
                    # pass did not, so the merge dedupes onto the real one.
                    if src not in nodes:
                        add_node(src, node.name, "code", rel, f"L{node.lineno}")
                    add_edge(src, tgt, "implements", source_file=rel, loc=f"L{node.lineno}")
                    marker_edges += 1

print(f"requirement-evidence edges from @pytest.mark.req: {marker_edges}")
if unknown_reqs:
    print(f"WARNING: markers naming undefined requirements: {sorted(unknown_reqs)}")

OUT.write_text(json.dumps({
    "nodes": list(nodes.values()),
    "edges": edges,
    "hyperedges": hyperedges,
    "input_tokens": 0,
    "output_tokens": 0,
}, indent=1, ensure_ascii=False), encoding="utf-8")

reqs = sum(1 for n in nodes.values() if re.match(r"^(FR|NFR)-", n["label"]))
oqs = sum(1 for n in nodes.values() if n["label"].startswith("OQ-"))
adrs = sum(1 for n in nodes.values() if n["label"].startswith("ADR-"))
print(
    f"docs nodes: {len(nodes)}  (requirements {reqs}, open questions {oqs}, "
    f"ADRs {adrs}, documents {len(files)})"
)
print(f"docs edges: {len(edges)}")
