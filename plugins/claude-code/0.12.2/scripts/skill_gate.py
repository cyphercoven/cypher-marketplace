#!/usr/bin/env python3
"""skill_gate.py — S-52..S-54: load the right skill before the work it owns.

PURPOSE
-------
Reads skills/triggers.yaml (the one trigger table) and acts as the Claude Code plugin hook:
  pre      PreToolUse: deny a call whose matched skill is not loaded in this session
  post     PostToolUse: record a Skill load; after a merge result that needs it, say "load cypher-mirror"
  session  SessionStart: one additionalContext line telling the agent to load cypher-workflow
Hook formats: https://code.claude.com/docs/en/hooks (fetched 2026-10-30): PreToolUse stdout
`hookSpecificOutput.permissionDecision: deny` + reason, exit 0; SessionStart / PostToolUse
`hookSpecificOutput.additionalContext`.

CONVENTIONS
-----------
- `match_rows`, `decide_pre`, `post_context`, `session_context` are pure. State and stdio are at
  the edge (`read_loaded`, `record_skill`, `reset`, `main`).
- State is one JSON file per session_id under ${CLAUDE_PLUGIN_DATA:-${XDG_STATE_HOME:-~/.local/state}/cypher-plugin};
  nothing is written to a repo.
- Fail open: an unreadable state file or bad hook input prints a warning on stderr and allows the call.
  A hook bug must never block all work.
- Typing `/skill-name` bypasses PreToolUse and PostToolUse, so such a load is not recorded; the agent
  loads it again through the Skill tool and is then let through.

AGENT NOTES
-----------
- The same table drives the gateway (tJ2) and the seat hook (tJ3); change rows in skills/triggers.yaml only.
- Needs PyYAML (also used by the other scripts here).
"""
import fnmatch
import json
import os
import pathlib
import re
import sys

TABLE = pathlib.Path(__file__).resolve().parent.parent / "skills" / "triggers.yaml"
SESSION_LINE = ("Cypher: for any work on the Cypher Suite or a cypher* repo, "
                "load the cypher-workflow skill first, before anything else.")
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit", "workspace_edit", "workspace_write"}
RESET_SOURCES = {"clear", "compact"}


# ---- pure core -------------------------------------------------------------------------

def norm_skill(name):
    return str(name).rsplit(":", 1)[-1]


def bare_tool(name):
    m = re.match(r"mcp__.+?__(.+)$", name)
    return m.group(1) if m else name


def glob_regex(pattern):
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def path_matches(pattern, path):
    path = path.replace("\\", "/")
    if "/" not in pattern:
        return fnmatch.fnmatchcase(path.rsplit("/", 1)[-1], pattern)
    rx = glob_regex(pattern)
    parts = path.split("/")
    return any(rx.match("/".join(parts[i:])) for i in range(len(parts)))


def event_paths(tool_name, tool_input):
    if bare_tool(tool_name) not in EDIT_TOOLS:
        return []
    return [str(tool_input[k]) for k in ("file_path", "path", "notebook_path") if tool_input.get(k)]


def _text(result):
    return result if isinstance(result, str) else json.dumps(result, default=str)


def row_matches(row, tool_name, tool_input, result=None):
    """True when every key in row['when'] matches; a result key needs a result."""
    when = row["when"]
    tool_input = tool_input or {}
    if "paths" in when and not any(path_matches(p, f) for p in when["paths"] for f in event_paths(tool_name, tool_input)):
        return False
    if "tools" in when and not any(fnmatch.fnmatchcase(n, p) for p in when["tools"] for n in (tool_name, bare_tool(tool_name))):
        return False
    if "input_has" in when and not any(tool_input.get(k) for k in when["input_has"]):
        return False
    if "commands" in when:
        cmd = str(tool_input.get("command", "")) if tool_name == "Bash" else ""
        if not any(re.search(p, cmd) for p in when["commands"]):
            return False
    if "result_contains" in when and (result is None or not re.search(when["result_contains"], _text(result))):
        return False
    return True


def match_rows(rows, tool_name, tool_input, result=None):
    if tool_name == "Skill":
        return []
    return [r for r in rows if row_matches(r, tool_name, tool_input, result)]


def _load_phrase(row):
    ref = f" and read {row['skill']}/{row['reference']}" if row.get("reference") else ""
    return f"{row['skill']}{ref}"


def decide_pre(rows, tool_name, tool_input, loaded):
    """Deny reason when a matched skill is not loaded, else None. Rows needing a result never block."""
    hits = [r for r in match_rows(rows, tool_name, tool_input) if "result_contains" not in r["when"]]
    missing = [r for r in hits if r["skill"] not in loaded]
    if not missing:
        return None
    todo = "; ".join(dict.fromkeys(_load_phrase(r) for r in missing))
    return f"Load before this call (Skill tool): {todo}. Then repeat the call."


def post_context(rows, tool_name, tool_input, result, loaded):
    """Context line when a result says a skill is needed next, else None."""
    hits = [r for r in match_rows(rows, tool_name, tool_input, result)
            if "result_contains" in r["when"] and r["skill"] not in loaded]
    if not hits:
        return None
    return "Load now (Skill tool): " + "; ".join(dict.fromkeys(_load_phrase(r) for r in hits)) + "."


def session_context(source):
    return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": SESSION_LINE}}


# ---- edge: state files ------------------------------------------------------------------

def warn(msg):
    print(f"skill-gate: {msg}", file=sys.stderr)


def state_dir():
    base = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not base:
        xdg = os.environ.get("XDG_STATE_HOME") or os.path.expanduser("~/.local/state")
        base = os.path.join(xdg, "cypher-plugin")
    path = pathlib.Path(base) / "skill-gate"
    path.mkdir(parents=True, exist_ok=True)
    return path


def state_file(session_id):
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(session_id)).lstrip(".") or "unknown"
    return state_dir() / f"{safe}.json"


def read_loaded(session_id):
    """Set of loaded skills; empty if never recorded; None (after a warning) if unreadable."""
    try:
        path = state_file(session_id)
        if not path.exists():
            return set()
        return {norm_skill(s) for s in json.loads(path.read_text())["loaded"]}
    except Exception as e:  # fail open
        warn(f"state unreadable ({e}); allowing")
        return None


def record_skill(session_id, skill):
    loaded = read_loaded(session_id) or set()
    loaded.add(norm_skill(skill))
    state_file(session_id).write_text(json.dumps({"loaded": sorted(loaded)}))


def reset(session_id):
    state_file(session_id).write_text(json.dumps({"loaded": []}))


# ---- edge: hook entry points ------------------------------------------------------------

def load_rows():
    import yaml
    return yaml.safe_load(TABLE.read_text())["rows"]


def _emit(obj):
    print(json.dumps(obj))


def run_pre(ev):
    loaded = read_loaded(ev.get("session_id", ""))
    if loaded is None:
        return
    reason = decide_pre(load_rows(), ev.get("tool_name", ""), ev.get("tool_input") or {}, loaded)
    if reason:
        _emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                      "permissionDecisionReason": reason}})


def run_post(ev):
    sid, name, tin = ev.get("session_id", ""), ev.get("tool_name", ""), ev.get("tool_input") or {}
    if name == "Skill":
        if tin.get("skill"):
            record_skill(sid, tin["skill"])
        return
    loaded = read_loaded(sid)
    if loaded is None:
        return
    ctx = post_context(load_rows(), name, tin, ev.get("tool_response"), loaded)
    if ctx:
        _emit({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": ctx}})


def run_session(ev):
    if ev.get("source") in RESET_SOURCES and ev.get("session_id"):
        reset(ev["session_id"])  # the context was wiped, so the skills must be loaded again
    _emit(session_context(ev.get("source")))


def main(argv):
    modes = {"pre": run_pre, "post": run_post, "session": run_session}
    if len(argv) != 1 or argv[0] not in modes:
        print("usage: skill_gate.py pre|post|session  (hook JSON on stdin)", file=sys.stderr)
        return 2
    try:
        ev = json.load(sys.stdin)
        modes[argv[0]](ev)
    except Exception as e:  # fail open: never block work on a hook bug
        warn(f"{argv[0]} failed ({type(e).__name__}: {e}); allowing")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
