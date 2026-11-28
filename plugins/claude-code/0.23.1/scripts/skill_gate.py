#!/usr/bin/env python3
"""skill_gate.py — S-52..S-54: load the right skill before the work it owns.

PURPOSE
-------
Reads skills/triggers.yaml (the one trigger table) and acts as the Claude Code plugin hook:
  pre      PreToolUse: deny a call whose matched skill is not loaded in this session
  post     PostToolUse: record a Skill load (the Skill tool, or a plain read of this plugin's own
           skills/<skill>/SKILL.md for hosts with no Skill tool, e.g. Codex); after a result that needs a skill (a `result_contains` row), say "load <skill>"
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
- Runtime uses only the standard library. make manifests compiles the YAML table to JSON.
"""
import fnmatch
import json
import os
import pathlib
import re
import shlex
import sys

TABLE = pathlib.Path(__file__).resolve().parent.parent / "skills" / "triggers.json"
SESSION_LINE = ("Cypher: for any work on the Cypher Suite or a cypher* repo, "
                "load the cypher-workflow skill first, before anything else.")
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit", "workspace_edit", "workspace_write"}
RESET_SOURCES = {"clear", "compact"}
# Shell tools whose completed call may be a plain read of a SKILL.md. Codex has no Skill tool and
# loads skills by `cat`; the name of its shell tool in the hook payload is undocumented (the S35C
# receipt shows `exec_command`), so the set is frozen here and widened only on evidence.
SHELL_TOOLS = frozenset({"Bash", "exec_command", "shell", "local_shell"})
SHELL_WRAPPERS = frozenset({"bash", "sh", "zsh"})
SHELL_META = re.compile(r"[|&;<>`$(){}*?~!\\\n\r]")
LINE_RANGE = re.compile(r"\d+(?:,\d+)?p\Z")


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
        cmd = str(tool_input.get("cmd", "")) if bare_tool(tool_name) == "workspace_exec" else (
            str(tool_input.get("command", "")) if tool_name in {"Bash", "PowerShell"} else "")
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
    return f"Load before this call (Skill tool, or read its SKILL.md): {todo}. Then repeat the call."


def post_context(rows, tool_name, tool_input, result, loaded):
    """Context line when a result says a skill is needed next, else None."""
    hits = [r for r in match_rows(rows, tool_name, tool_input, result)
            if "result_contains" in r["when"] and r["skill"] not in loaded]
    if not hits:
        return None
    return "Load now (Skill tool): " + "; ".join(dict.fromkeys(_load_phrase(r) for r in hits)) + "."


def _command_argv(cmd):
    """argv for a single plain command, or None. A string with any shell metacharacter is refused."""
    if isinstance(cmd, list):
        if not cmd or not all(isinstance(a, str) for a in cmd):
            return None
        if len(cmd) == 3 and os.path.basename(cmd[0]) in SHELL_WRAPPERS and cmd[1] in {"-c", "-lc"}:
            return _command_argv(cmd[2])
        return cmd
    if not isinstance(cmd, str) or SHELL_META.search(cmd):
        return None
    try:
        return shlex.split(cmd)
    except ValueError:
        return None


def _read_operand(argv):
    """The one path a read-only cat / nl / head / sed -n argv reads, else None."""
    if not argv:
        return None
    prog, args = os.path.basename(argv[0]), argv[1:]
    if prog in {"cat", "nl"} and len(args) == 1:
        return args[0]
    if prog == "head" and (len(args) == 1 or
                           (len(args) == 2 and re.fullmatch(r"-\d+", args[0])) or
                           (len(args) == 3 and args[0] == "-n" and args[1].isdigit())):
        return args[-1]
    if prog == "sed" and len(args) == 3 and args[0] == "-n" and LINE_RANGE.match(args[1]):
        return args[2]
    return None


def skill_from_read(tool_name, tool_input, plugin_root):
    """Skill name when the call is a plain read of <plugin_root>/skills/<skill>/SKILL.md, else None.

    realpath on both sides defeats `..` and symlink escapes; the relative path must then be
    exactly skills/<skill>/SKILL.md. Pure apart from the filesystem lookup realpath makes.
    """
    tin = tool_input if isinstance(tool_input, dict) else {}
    if tool_name == "Read":
        path = tin.get("file_path")
    elif tool_name in SHELL_TOOLS:
        path = _read_operand(_command_argv(tin.get("command", tin.get("cmd"))))
    else:
        return None
    if not isinstance(path, str) or not os.path.isabs(path):
        return None
    real = os.path.realpath(path)
    parts = os.path.relpath(real, os.path.realpath(plugin_root)).split(os.sep)
    if len(parts) == 3 and parts[0] == "skills" and parts[2] == "SKILL.md" and parts[1] not in {"", ".", ".."} \
            and os.path.isfile(real):
        return parts[1]
    return None


def response_failed(response):
    """True when a tool response reports an error or a nonzero exit."""
    if isinstance(response, dict):
        if response.get("is_error") or response.get("isError") or response.get("error"):
            return True
        for key in ("exit_code", "exitCode", "returncode"):
            code = response.get(key)
            if isinstance(code, int) and not isinstance(code, bool) and code != 0:
                return True
        return response_failed(response.get("metadata")) if isinstance(response.get("metadata"), dict) else False
    if isinstance(response, str):
        if re.match(r"\s*Error", response):
            return True
        m = re.match(r"\s*Exit code:?\s*(\d+)", response)
        return bool(m and int(m.group(1)))
    return False


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

def plugin_root():
    """CLAUDE_PLUGIN_ROOT, else the directory above this script."""
    return pathlib.Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or pathlib.Path(__file__).resolve().parent.parent).resolve()


def load_rows():
    return json.loads(TABLE.read_text())["rows"]


def _emit(obj):
    print(json.dumps(obj))


def lifecycle_failure_reason(ev):
    """Narrow packaging/error fallback: block execution transitions, leave repair available."""
    name, args = ev.get("tool_name", ""), ev.get("tool_input") or {}
    command = str(args.get("command", args.get("cmd", "")))
    launch = name in {"Agent", "Task"} and args.get("subagent_type") not in {"Plan", "Explore"}
    if (launch or bare_tool(name) in {"forgejo_pr_merge", "production_admission", "improve_production_admission"}
            or re.search(r"factory/bin/seat[.]sh(?:\s|$)", command)):
        return "Improve checkpoint validator unavailable; load cypher-improve and repair installation/evidence before this transition. Reads and planning remain available."
    return None


def run_pre(ev):
    # Lifecycle evidence is a separate fail-closed transition gate, not a skill-load boolean.
    try:
        import improve_checkpoint
        reason = improve_checkpoint.hook_decision(ev)
    except Exception:
        reason = lifecycle_failure_reason(ev)
    if reason:
        _emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                      "permissionDecisionReason": reason}})
        return
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
    skill = skill_from_read(name, tin, plugin_root())
    if skill and not response_failed(ev.get("tool_response")):
        record_skill(sid, skill)  # a host with no Skill tool loads a skill by reading its SKILL.md
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
    ev = {}
    try:
        ev = json.load(sys.stdin)
        modes[argv[0]](ev)
    except Exception as e:
        reason = lifecycle_failure_reason(ev) if argv[0] == "pre" and isinstance(ev, dict) else None
        if reason:
            _emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                          "permissionDecisionReason": reason}})
        else:
            warn(f"{argv[0]} failed ({type(e).__name__}); allowing non-lifecycle work")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
