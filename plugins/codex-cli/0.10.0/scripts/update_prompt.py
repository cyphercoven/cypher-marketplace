#!/usr/bin/env python3
"""update_prompt.py — S-21: tell the person once when a release needs /cypher-setup re-run.

PURPOSE
-------
Compares the person's saved `answers_version` (settings record) with the newest
CHANGELOG entry flagged `needs-setup: true` that also carries `answers_version: N`
(the template version that release needs). Older -> one line: "Your Cypher
instructions changed — run /cypher-setup". "Once" = the required version that was
announced is remembered in a small local state file.

CONVENTIONS
-----------
- `newest_required`, `should_announce`, `hook_output` (given state + changelog text)
  are pure; only `load_state`/`save_state`/`main` touch disk.
- State file: `$PLUGIN_DATA`/`$CLAUDE_PLUGIN_DATA` + `/update-state.json`, else
  `~/.config/cypher/update-state.json`. Keys: answers_version, announced_for.
- A SessionStart hook cannot call MCP tools, so it reads the answers_version that
  `cypher-start` last recorded here (`record`); with none recorded it stays silent.

AGENT NOTES
-----------
- CLI: `hook` (SessionStart; prints hook JSON or nothing), `record --answers-version N`,
  `check --answers-version N` (prints the line and marks it announced, exit 0 either way).
- Stdlib only.
"""
import argparse
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MESSAGE = "Your Cypher instructions changed — run /cypher-setup"
_ANSWERS_RE = re.compile(r"^\s*answers_version:\s*(\d+)\s*$", re.MULTILINE)
_FLAG_RE = re.compile(r"^\s*needs-setup:\s*true\s*$", re.MULTILINE)


def newest_required(changelog_text: str) -> int | None:
    """Pure: answers_version of the newest `## ` section flagged needs-setup (sections run newest first)."""
    for section in re.split(r"^## ", changelog_text, flags=re.MULTILINE)[1:]:
        if _FLAG_RE.search(section):
            m = _ANSWERS_RE.search(section)
            if m:
                return int(m.group(1))
    return None


def should_announce(answers_version: int | None, required: int | None, announced_for: int | None) -> bool:
    if answers_version is None or required is None:
        return False
    return answers_version < required and announced_for != required


def hook_output(state_path: pathlib.Path, changelog_text: str) -> str:
    """SessionStart hook stdout: JSON with a user-visible systemMessage, or '' when nothing to say."""
    state = load_state(state_path)
    required = newest_required(changelog_text)
    if not should_announce(state.get("answers_version"), required, state.get("announced_for")):
        return ""
    save_state(state_path, {**state, "announced_for": required})
    return json.dumps({"systemMessage": MESSAGE})


def check(state_path: pathlib.Path, changelog_text: str, answers_version: int | None) -> bool:
    """For hosts without hooks (cypher-start): True once when the line should be said."""
    state = load_state(state_path)
    required = newest_required(changelog_text)
    if not should_announce(answers_version, required, state.get("announced_for")):
        return False
    save_state(state_path, {**state, "answers_version": answers_version, "announced_for": required})
    return True


def record_answers(state_path: pathlib.Path, answers_version: int) -> None:
    save_state(state_path, {**load_state(state_path), "answers_version": answers_version})


def load_state(path: pathlib.Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save_state(path: pathlib.Path, state: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state))
    except OSError:
        pass  # a prompt must never break a session


def default_state_path() -> pathlib.Path:
    base = os.environ.get("PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    if base:
        return pathlib.Path(base) / "update-state.json"
    return pathlib.Path.home() / ".config" / "cypher" / "update-state.json"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["hook", "record", "check"])
    ap.add_argument("--answers-version", type=int)
    ap.add_argument("--state-file", type=pathlib.Path, default=None)
    ap.add_argument("--changelog", type=pathlib.Path, default=ROOT / "CHANGELOG.md")
    a = ap.parse_args(argv)
    state = a.state_file or default_state_path()
    try:
        text = a.changelog.read_text()
    except OSError:
        text = ""
    if a.cmd == "hook":
        out = hook_output(state, text)
        if out:
            print(out)
    elif a.cmd == "record":
        if a.answers_version is None:
            ap.error("record needs --answers-version")
        record_answers(state, a.answers_version)
    else:
        if check(state, text, a.answers_version):
            print(MESSAGE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
