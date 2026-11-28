#!/usr/bin/env python3
"""setup_render.py — S-15..S-19: the deterministic core behind /cypher-admin setup.

PURPOSE
-------
Pure functions the cypher-setup skill tells the agent to run: which questions to ask and their
prefills, whether to offer "keep previous answers", answers <-> settings record mapping, the
rendered instructions, the host's paste location, and the write plan (target path + diff) for
CLI hosts. The agent does the talking and the gateway calls; this file does the arithmetic.

CONVENTIONS
-----------
- Everything except `main()` is pure. `main()` is the only edge: it reads JSON/YAML files named on
  the command line and prints JSON or text. It never writes the target file (the skill does, after a confirm).
- Rendering is delegated to render_template.render so `make render-template` and setup agree.
- Record mapping: display_name <- owner_name, pronouns <- "subject/object", providers, hosts,
  answers_version <- templates/variables.yaml `version`; every other answer lives in `work_style`.

AGENT NOTES
-----------
- Run via `uv run --with pyyaml==6.0.2 scripts/setup_render.py <command> ...` (see the skill).
- Commands: questions | mode | record | render | host | plan  (each takes --help).
"""
import argparse
import difflib
import json
import pathlib
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import render_template  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIRECT = {"owner_name": "display_name", "providers": "providers"}
# client names as the gateway's onboarding reports them (and the agent CLIs call themselves) -> hosts.yaml id
CLIENTS = {
    "claude-code": "claude-code", "claude": "claude-code", "claude-ai": "claude-ai",
    "claude-desktop": "claude-desktop", "cowork": "cowork",
    "codex": "codex-cli", "codex-cli": "codex-cli", "chatgpt": "chatgpt-desktop", "chatgpt-desktop": "chatgpt-desktop",
    "antigravity": "antigravity", "agy": "antigravity",
    "copilot": "vscode-copilot", "vscode-copilot": "vscode-copilot", "cursor": "cursor",
    "gemini-app": "gemini-app",
}


def detect_host(client: str):
    return CLIENTS.get((client or "").strip().lower())


def from_record(record: dict) -> dict:
    """Settings record -> answers dict (inverse of to_record)."""
    answers = dict(record.get("work_style") or {})
    if record.get("display_name"):
        answers["owner_name"] = record["display_name"]
    if record.get("pronouns"):
        answers["pronoun_subject"] = record["pronouns"].split("/")[0]
    if record.get("providers") is not None:
        answers["providers"] = record["providers"]
    return answers


def to_record(answers: dict, spec: dict, host_id: str) -> dict:
    """Answers -> settings_set fields, stamped with the template version."""
    vals = render_template.values(answers, spec)
    rest = {k: v for k, v in answers.items() if k not in ("owner_name", "pronoun_subject", "providers")}
    return {
        "display_name": answers["owner_name"],
        "pronouns": vals["pronouns"],
        "work_style": rest,
        "providers": answers.get("providers", []),
        "hosts": [host_id],
        "answers_version": spec["version"],
    }


def mode(record, spec: dict) -> str:
    """full = ask everything (no usable record); ask-keep = the single keep-or-full question;
    ask-keep-stale = same, but the saved answers predate the current template version."""
    if not record or record.get("answers_version") is None:
        return "full"
    return "ask-keep" if record["answers_version"] == spec["version"] else "ask-keep-stale"


def questions(spec: dict, record, host_details: dict) -> list:
    """Each question with its prefill: saved answer > host user detail > declared default > None."""
    saved = from_record(record) if record else {}
    out = []
    for v in spec["variables"]:
        n = v["name"]
        prefill = saved.get(n, host_details.get(n, v.get("default")))
        out.append({k: v[k] for k in ("name", "question", "type", "choices") if k in v} | {"prefill": prefill})
    return out


def render_text(template: str, answers: dict, spec: dict) -> str:
    return render_template.render(template, answers, spec)


def paste_location(hosts: dict, host_id: str) -> dict:
    h = hosts[host_id]
    return {"host": host_id, "name": h["name"], "location": h["location"], "can_write_file": h["can_write_file"]}


def write_plan(hosts: dict, host_id: str, new_text: str, old_text):
    """None unless the host lets the agent write; else target path + unified diff (old_text None = new file)."""
    h = hosts[host_id]
    if not h.get("can_write_file"):
        return None
    path = h["target_path"]
    diff = "".join(difflib.unified_diff((old_text or "").splitlines(True), new_text.splitlines(True),
                                        f"a/{path}", f"b/{path}"))
    return {"target_path": path, "creates": old_text is None, "diff": diff}


def _load(p):
    return yaml.safe_load(pathlib.Path(p).read_text()) if p else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, flags in {
        "questions": ["--record", "--host-details"], "mode": ["--record"], "record": ["--answers", "--host"],
        "render": ["--answers"], "host": ["--host", "--client"], "plan": ["--answers", "--host", "--existing"],
    }.items():
        p = sub.add_parser(name)
        for f in flags:
            p.add_argument(f)
    a = ap.parse_args()
    spec = _load(ROOT / "templates" / "variables.yaml")
    hosts = _load(ROOT / "templates" / "hosts.yaml")["hosts"]
    template = (ROOT / "templates" / "project-instructions.md").read_text()
    out = lambda o: print(json.dumps(o, indent=2, default=str))  # noqa: E731
    if a.cmd == "questions":
        out(questions(spec, _load(a.record), _load(a.host_details) or {}))
    elif a.cmd == "mode":
        out(mode(_load(a.record), spec))
    elif a.cmd == "record":
        out(to_record(_load(a.answers), spec, a.host))
    elif a.cmd == "render":
        sys.stdout.write(render_text(template, _load(a.answers), spec))
    elif a.cmd == "host":
        hid = a.host or detect_host(a.client)
        if not hid:
            out({"host": None, "known_hosts": {k: v["name"] for k, v in hosts.items()}})
        else:
            out(paste_location(hosts, hid))
    elif a.cmd == "plan":
        text = render_text(template, _load(a.answers), spec)
        old = pathlib.Path(a.existing).expanduser().read_text() if a.existing and pathlib.Path(a.existing).expanduser().exists() else None
        out(write_plan(hosts, a.host, text, old))
    return 0


if __name__ == "__main__":
    sys.exit(main())
