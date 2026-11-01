#!/usr/bin/env python3
"""check_skills.py — S-45: every skill is one job, <=300 lines, one trigger section.

PURPOSE
-------
Fails when a skills/<name>/SKILL.md is over 300 lines, has a `name` that is
not its directory (and `cypher-` prefixed), has a description with no
trigger phrase ("use when", "when", "trigger"), or has more than one
trigger section heading, or uses a host-only term from
config/host-only-terms.txt (S-60). A skill that outgrows this splits into named
`cypher-` skills instead of growing.

CONVENTIONS
-----------
- `evaluate(dirname, text)` is pure and returns a list of error strings;
  `check_repo(root)` and `main()` are the file I/O.

AGENT NOTES
-----------
- Stdlib only. Wired as `make check-skills` and part of `make check`.
"""
import pathlib
import re
import sys

MAX_LINES = 300
# The `/` menu holds only these two commands; every other skill is model-invocable and hidden from it.
MENU_SKILLS = ("cypher-admin", "cypher-legal")
# `/cypher-admin <sub-command>` -> the skill it loads. The cypher-admin table must list each pair.
ADMIN_ROUTES = {
    "setup": "cypher-setup", "start": "cypher-start", "afk": "cypher-afk", "spec": "cypher-spec",
    "design": "cypher-design", "deploy": "cypher-deploy", "build-app": "cypher-build-app",
    "handover": "cypher-handover", "troubleshoot": "cypher-troubleshoot", "mirror": "cypher-mirror",
    "media": "cypher-media", "secrets": "cypher-secrets", "ops": "cypher-ops", "review": "cypher-review",
    "workflow": "cypher-workflow",
}
TRIGGER_HEADING = re.compile(r"^##\s+(?:\d+\.\s*)?(?:when\b|triggers?\b)", re.IGNORECASE)
TRIGGER_WORD = re.compile(r"\b(use when|when|whenever|before|triggers?)\b", re.IGNORECASE)


def _frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return lines[1:i]
    return None


def _field(front, key):
    for line in front:
        m = re.match(rf"{key}:\s*(.*)$", line)
        if m:
            return m.group(1).strip().strip("\"'")
    return ""


def parse_terms(text):
    """Pure: term-file text -> (compiled host-only regexes, exempt skill names)."""
    terms, exempt = [], set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("exempt:"):
            exempt.add(line.split(":", 1)[1].strip())
        else:
            terms.append(re.compile(line, re.IGNORECASE))
    return terms, exempt


def load_terms(root):
    return parse_terms(pathlib.Path(root, "config", "host-only-terms.txt").read_text())


def host_term_errors(dirname, text, terms, exempt):
    if dirname in exempt:
        return []
    hits = sorted({m.group(0) for t in terms for m in t.finditer(text)})
    return [f"{dirname}: host-only term '{h}' — move it to hosts/<host>.md" for h in hits]


def evaluate(dirname, text, terms=(), exempt=frozenset()):
    errors = host_term_errors(dirname, text, terms, exempt)
    n = len(text.splitlines())
    if n > MAX_LINES:
        errors.append(f"{dirname}: {n} lines, over the {MAX_LINES} limit — split it into named cypher- skills")
    front = _frontmatter(text)
    if front is None:
        return errors + [f"{dirname}: no frontmatter"]
    name = _field(front, "name")
    if name != dirname:
        errors.append(f"{dirname}: name '{name}' must equal the directory")
    if not dirname.startswith("cypher-"):
        errors.append(f"{dirname}: skill names start with cypher-")
    if not TRIGGER_WORD.search(_field(front, "description")):
        errors.append(f"{dirname}: description has no trigger phrase (say when to load it)")
    triggers = [l for l in text.splitlines() if TRIGGER_HEADING.match(l)]
    if len(triggers) > 1:
        errors.append(f"{dirname}: {len(triggers)} trigger sections, want one")
    return errors


def user_invocable(text):
    """Pure: True when the skill shows in the `/` menu (frontmatter `user-invocable` is not `false`)."""
    return _field(_frontmatter(text) or [], "user-invocable").lower() != "false"


def invocation_errors(dirname, text):
    """Pure: the `/` menu is cypher-admin (command only) and cypher-legal (command and model); the rest are hidden."""
    front = _frontmatter(text) or []
    hidden = not user_invocable(text)
    command_only = _field(front, "disable-model-invocation").lower() == "true"
    if dirname not in MENU_SKILLS:
        errors = [] if hidden else [f"{dirname}: add `user-invocable: false` (only {', '.join(MENU_SKILLS)} show in the / menu)"]
        if command_only:
            errors.append(f"{dirname}: must stay model-invocable (triggers and gates look skills up by name)")
        return errors
    errors = []
    if hidden:
        errors.append(f"{dirname}: must show in the / menu (no `user-invocable: false`)")
    if not _field(front, "argument-hint"):
        errors.append(f"{dirname}: missing argument-hint")
    if (dirname == "cypher-admin") != command_only:
        errors.append(f"{dirname}: disable-model-invocation must be {'true' if dirname == 'cypher-admin' else 'absent'}")
    return errors


def admin_route_errors(text, skills):
    """Pure: the cypher-admin table lists every sub-command with its skill, and each skill exists."""
    rows = set(re.findall(r"^\|\s*`([a-z-]+)`\s*\|\s*`(cypher-[a-z-]+)`", text, re.MULTILINE))
    errors = [f"cypher-admin: no `{k}` -> `{v}` row" for k, v in ADMIN_ROUTES.items() if (k, v) not in rows]
    return errors + [f"cypher-admin: routes to missing skill {v}" for v in ADMIN_ROUTES.values() if v not in skills]


def check_repo(root):
    errors = []
    terms, exempt = load_terms(root)
    paths = sorted(pathlib.Path(root, "skills").glob("*/SKILL.md"))
    skills = {p.parent.name for p in paths}
    for path in paths:
        text = path.read_text()
        errors += evaluate(path.parent.name, text, terms, exempt) + invocation_errors(path.parent.name, text)
        if path.parent.name == "cypher-admin":
            errors += admin_route_errors(text, skills)
    errors += [f"{m}: skill missing" for m in MENU_SKILLS if m not in skills]
    return errors


def main():
    errors = check_repo(pathlib.Path(__file__).resolve().parent.parent)
    for e in errors:
        print("FAIL", e)
    print(f"check-skills: {'FAIL' if errors else 'ok'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
