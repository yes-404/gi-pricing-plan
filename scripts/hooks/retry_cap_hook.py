#!/usr/bin/env python3
"""C2 -- the retry-cap hook (RFC-895 §2 item C2; RL-920 §4 and §6; RL-907(a)/(c)).

`docs/rulings/RL-00920-q2-is-answered-differently-for-c2-and-c3-c3-is-dissolved-c2-gets-claude-settings-json-and-slice-g-is-re-cut-and-still-blocked.md`, RL-920 §4,
distinguishes C2 from C3 (dissolved): C3 would have re-checked a state already written
down and already checked more strongly by CI, but C2 "genuinely needs a hook" because it
**intercepts an action that leaves no artifact** -- blocking the next retry at the moment
a fix/replan decision is recorded, per `docs/process/delivery-process.md` §7: "On breach,
the loop pauses and notifies a human instead of retrying again."

Two entry points, sharing one decision function (`_would_breach`) so the dry-run and the
doer can never disagree:

- `record` -- the command a role runs to record a fix/replan decision against a layer
  (RFC-895 impact-matrix row 11: recording a fix/replan decision updates the retry
  counter in the runtime state file "via hook C2, not by hand"). On success, increments
  `retry_counters[<layer>:<id>:<kind>].count` in the runtime state file (RFC-895 artifact
  B, `.claude/skills/watcher-runtime-state`). On a would-be breach of
  `docs/process/delivery-process.core.json`'s `guards.retry_caps.values[<layer>]`,
  **refuses** -- exit 1, the counter is left untouched because the retry did not happen
  -- and writes `pending_human_checkpoint`, the durable half of "notifies a human".
  `record`'s own refusal is unconditional: it enforces the cap whether or not it is
  reached through the registered hook below, because a script's own logic cannot be
  switched off the way a settings-file hook can.
- `hook` -- the Claude Code PreToolUse entry point registered in `.claude/settings.json`.
  Reads the tool-call JSON Claude Code hands it on stdin; if the pending Bash command is
  a `record` invocation that would breach, denies the tool call before it ever runs (so
  the underlying `record` command -- and the turn it would have cost -- never executes)
  and writes the same `pending_human_checkpoint` entry, because in this path `record`
  itself never runs to write it. A command `hook` cannot confidently parse as a `record`
  invocation is allowed through unparsed -- a mis-parse must never falsely block, only a
  confirmed breach may.

What C2 can and cannot guarantee (stated plainly, per RL-920 §3/§5's standard for a
hook -- a check proven only by hand is one that has never printed a failure, and a
git-hook-style guarantee that can be silently skipped is not a guarantee):

- **Can:** if a retry is recorded through `record` -- directly, or via the Bash tool
  while hooks are active -- the cap in artifact A binds at that exact moment; a breach is
  refused and a durable notification is written to artifact B.
- **Cannot:** stop an actor from skipping `record` and hand-editing the runtime state
  file's `retry_counters` block directly, from disabling hooks for a session
  (`disableAllHooks`, or an override in the gitignored `.claude/settings.local.json`), or
  from never recording a retry at all. Unlike C3 (dissolved by RL-920 because no
  stronger backstop existed for a git hook -- CI already re-checks the same state), there
  is **no CI-equivalent backstop behind C2**: nothing in this repository re-derives retry
  counts from durable artifacts (RL-907(b) assigns that reconciliation to a future
  watcher cycle, not built in this slice). C2's enforcement is real at the moment it
  fires and has no second line of defence.

`kind` is restricted to the two vocabulary strings `docs/process/delivery-process.core.
json` already uses for a `retry_cap`-guarded transition -- `replan` (`vocabularies.
plan_gate_decision`, `flows.map_layer_flow.plan_gate.transitions.replan`) and `fix`
(`vocabularies.audit_verdict_proposal`, the `verdict.transitions.fix` guard repeated at
both the map-layer and slice-layer flows). This is deliberately narrower than every
`guarded_by: "retry_cap"` transition in the extract: `slice_tdd_flow.verify_refactor`'s
`failure` transition and `guards.retry_caps.instrumentation`'s "gate re-runs" entry are
RL-907(a)'s explicitly **uncapped** class ("Gate re-runs are logged and not capped, so
nothing blocks on them") and are out of this slice's scope.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA = "gi-pricing-plan-runtime-state"
SCHEMA_VERSION = 1
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE_FILE = Path.home() / "gi-pricing-plan.local" / "handover" / "runtime-state.json"
DEFAULT_CORE_FILE = ROOT / "docs" / "process" / "delivery-process.core.json"
_TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
_KNOWN_KINDS = ("replan", "fix")


def _now_iso() -> str:
    return datetime.now(UTC).strftime(_TS_FORMAT)


def _state_file_path(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    override = os.environ.get("RUNTIME_STATE_FILE")
    return Path(override) if override else DEFAULT_STATE_FILE


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    try:
        loaded: dict[str, Any] = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"runtime state file is not valid JSON, refusing to touch it: {path} ({exc})"
        ) from exc
    return loaded


def _dump_state(doc: dict[str, Any]) -> str:
    return json.dumps(doc, indent=2, sort_keys=False, ensure_ascii=False) + "\n"


def _write_state(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_dump_state(doc), encoding="utf-8")


def _load_cap(core_file: Path, layer: str) -> int:
    if not core_file.exists():
        raise SystemExit(f"core extract not found, refusing to guess a cap: {core_file}")
    core = json.loads(core_file.read_text(encoding="utf-8"))
    values = core.get("guards", {}).get("retry_caps", {}).get("values", {})
    if layer not in values:
        raise SystemExit(
            f"unknown layer {layer!r}; {core_file} guards.retry_caps.values has no entry "
            f"for it (known: {sorted(values)})"
        )
    cap: int = values[layer]
    return cap


def _counter_key(layer: str, id_: str, kind: str) -> str:
    return f"{layer}:{id_}:{kind}"


def _current_count(state: dict[str, Any], key: str) -> int:
    entries = state.get("retry_counters", {}).get("entries", {})
    entry = entries.get(key)
    return int(entry["count"]) if entry else 0


def _would_breach(
    state: dict[str, Any], core_file: Path, layer: str, id_: str, kind: str
) -> tuple[bool, int, int]:
    """Returns (would_breach, current_count, cap). A breach is recording the (cap+1)-th
    event: the pending attempt is refused once the layer already carries `cap` recorded
    events for this key -- the negative control (`cap - 1` already recorded) must be
    allowed through and become `cap`, still within bound."""
    cap = _load_cap(core_file, layer)
    current = _current_count(state, _counter_key(layer, id_, kind))
    return current >= cap, current, cap


def _pending_checkpoint_block(
    layer: str, id_: str, kind: str, current: int, cap: int, evidence: str
) -> dict[str, Any]:
    return {
        "written_by": "hook:C2",
        "written_at": _now_iso(),
        "layer": layer,
        "id": id_,
        "kind": kind,
        "attempted_count": current + 1,
        "cap": cap,
        "reason": (
            f"retry cap breached: {layer}:{id_}:{kind} already carries {current} recorded "
            f"event(s) against a cap of {cap}; the loop pauses and a human must resolve "
            f"this before another {kind} is recorded (delivery-process.md §7)"
        ),
        "evidence": evidence,
    }


def _human_message(layer: str, id_: str, kind: str, current: int, cap: int) -> str:
    return (
        f"RETRY CAP BREACHED -- {layer}:{id_}:{kind} is at {current}/{cap}. "
        "The loop pauses here; a human must resolve it before another retry is recorded "
        "(docs/process/delivery-process.md §7)."
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--state-file", default=None)
    parser.add_argument("--core-file", default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    p_record = sub.add_parser("record", help="Record a fix/replan decision against a layer")
    p_record.add_argument("--layer", required=True)
    p_record.add_argument("--id", dest="id_", required=True)
    p_record.add_argument("--kind", required=True, choices=_KNOWN_KINDS)
    p_record.add_argument(
        "--evidence",
        required=True,
        help="Durable artifact this decision is grounded in (PR number, commit SHA, plan "
        "revision) -- RL-907(a): nothing that blocks an action may be counted without one.",
    )
    p_record.set_defaults(func=cmd_record)

    p_hook = sub.add_parser("hook", help="Claude Code PreToolUse entry point (reads stdin JSON)")
    p_hook.set_defaults(func=cmd_hook)

    p_clear = sub.add_parser(
        "clear-checkpoint", help="Clear pending_human_checkpoint once a human has resolved it"
    )
    p_clear.set_defaults(func=cmd_clear_checkpoint)

    return parser


def cmd_record(args: argparse.Namespace) -> int:
    state_path = _state_file_path(args.state_file)
    core_file = Path(args.core_file) if args.core_file else DEFAULT_CORE_FILE
    state = _load_state(state_path)

    breach, current, cap = _would_breach(state, core_file, args.layer, args.id_, args.kind)
    if breach:
        state["schema"] = state.get("schema", SCHEMA)
        state["schema_version"] = state.get("schema_version", SCHEMA_VERSION)
        state["project"] = state.get("project", "gi-pricing-plan")
        state["pending_human_checkpoint"] = _pending_checkpoint_block(
            args.layer, args.id_, args.kind, current, cap, args.evidence
        )
        _write_state(state_path, state)
        print(_human_message(args.layer, args.id_, args.kind, current, cap), file=sys.stderr)
        return 1

    key = _counter_key(args.layer, args.id_, args.kind)
    entries = dict(state.get("retry_counters", {}).get("entries", {}))
    prior = entries.get(key, {})
    history = list(prior.get("evidence", []))
    history.append({"at": _now_iso(), "evidence": args.evidence})
    entries[key] = {"count": current + 1, "evidence": history}

    state["schema"] = state.get("schema", SCHEMA)
    state["schema_version"] = state.get("schema_version", SCHEMA_VERSION)
    state["project"] = state.get("project", "gi-pricing-plan")
    state["retry_counters"] = {
        "written_by": "hook:C2",
        "written_at": _now_iso(),
        "entries": entries,
    }
    _write_state(state_path, state)
    print(f"recorded: {key} -> {current + 1}/{cap}")
    return 0


def _extract_record_invocation(command: str) -> dict[str, str] | None:
    """Parse a Bash command string for a `retry_cap_hook.py record ...` invocation.
    Returns None (never raises) on anything that does not confidently look like one --
    an unparsed command must be allowed through, not blocked."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    if "retry_cap_hook.py" not in " ".join(tokens):
        return None
    if "record" not in tokens:
        return None
    record_args = tokens[tokens.index("record") + 1 :]
    try:
        p_record = argparse.ArgumentParser()
        p_record.add_argument("--layer", required=True)
        p_record.add_argument("--id", dest="id_", required=True)
        p_record.add_argument("--kind", required=True, choices=_KNOWN_KINDS)
        p_record.add_argument("--evidence", required=True)
        parsed, _unknown = p_record.parse_known_args(record_args)
    except SystemExit:
        return None
    if parsed.layer is None or parsed.id_ is None or parsed.kind is None:
        return None
    return {"layer": parsed.layer, "id": parsed.id_, "kind": parsed.kind}


def _allow(reason: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": reason,
        }
    }


def _deny(reason: str, message: str) -> dict[str, Any]:
    return {
        "systemMessage": message,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }


def cmd_hook(args: argparse.Namespace) -> int:
    payload_text = sys.stdin.read()
    try:
        payload = json.loads(payload_text) if payload_text.strip() else {}
    except json.JSONDecodeError:
        print(json.dumps(_allow("unparseable hook payload, allowed through unexamined")))
        return 0

    command = payload.get("tool_input", {}).get("command", "")
    parsed = _extract_record_invocation(command)
    if parsed is None:
        print(json.dumps(_allow("not a recognised retry_cap_hook.py record invocation")))
        return 0

    state_path = _state_file_path(args.state_file)
    core_file = Path(args.core_file) if args.core_file else DEFAULT_CORE_FILE
    state = _load_state(state_path)
    layer, id_, kind = parsed["layer"], parsed["id"], parsed["kind"]
    breach, current, cap = _would_breach(state, core_file, layer, id_, kind)
    if not breach:
        print(json.dumps(_allow(f"{layer}:{id_}:{kind} at {current}/{cap}")))
        return 0

    state["schema"] = state.get("schema", SCHEMA)
    state["schema_version"] = state.get("schema_version", SCHEMA_VERSION)
    state["project"] = state.get("project", "gi-pricing-plan")
    state["pending_human_checkpoint"] = _pending_checkpoint_block(
        layer, id_, kind, current, cap, "blocked-by-hook-before-record-ran"
    )
    _write_state(state_path, state)
    message = _human_message(layer, id_, kind, current, cap)
    print(json.dumps(_deny(f"retry cap breach: {layer}:{id_}:{kind} at {current}/{cap}", message)))
    return 0


def cmd_clear_checkpoint(args: argparse.Namespace) -> int:
    state_path = _state_file_path(args.state_file)
    state = _load_state(state_path)
    if state.get("pending_human_checkpoint") is None:
        print("no pending human checkpoint to clear")
        return 0
    state["pending_human_checkpoint"] = None
    _write_state(state_path, state)
    print("cleared pending_human_checkpoint")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
