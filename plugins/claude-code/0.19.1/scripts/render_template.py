#!/usr/bin/env python3
"""render_template.py — S-14: render templates/project-instructions.md from answers.

PURPOSE
-------
Substitutes `{{name}}` and `{{#if name}}…{{/if}}` in the instructions
template using a fixture/answers YAML, with derived pronoun values (pronouns, pronoun_object, pronoun_possessive) from
templates/variables.yaml. `--fixture NAME` reads fixtures/NAME.yaml;
`--fixture-file PATH` reads any path (the owner's fixture lives outside the repo).

CONVENTIONS
-----------
- `render()` is pure (template text, answers, variables spec -> text).
  Unknown or missing variables raise; nothing is guessed.
- The leading `<!-- … -->` header of the template is documentation and is dropped.

AGENT NOTES
-----------
- Needs PyYAML (the Makefile target runs it through `uv run --with pyyaml`).
"""
import argparse
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
HEADER_RE = re.compile(r"\A\s*<!--.*?-->\s*\n", re.DOTALL)
IF_RE = re.compile(r"\{\{#if (\w+)\}\}(.*?)\{\{/if\}\}", re.DOTALL)
VAR_RE = re.compile(r"\{\{(\w+)\}\}")


def values(answers: dict, spec: dict) -> dict:
    """Pure: answers + declared defaults + derived values."""
    out = {v["name"]: v["default"] for v in spec["variables"] if "default" in v}
    out.update(answers)
    for name, rule in spec.get("derived", {}).items():
        src = out.get(rule["from"])
        if src not in rule:
            raise KeyError(f"cannot derive {name}: {rule['from']}={src!r}")
        out[name] = rule[src]
    out["pronouns"] = f"{out['pronoun_subject']}/{out['pronoun_object']}"
    return out


def render(template: str, answers: dict, spec: dict) -> str:
    vals = values(answers, spec)
    text = HEADER_RE.sub("", template, count=1)
    text = IF_RE.sub(lambda m: m.group(2) if vals.get(m.group(1)) else "", text)

    def sub(m):
        if m.group(1) not in vals:
            raise KeyError(f"no value for {{{{{m.group(1)}}}}}")
        return str(vals[m.group(1)])

    return VAR_RE.sub(sub, text)


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fixture")
    g.add_argument("--fixture-file")
    args = ap.parse_args()
    path = pathlib.Path(args.fixture_file) if args.fixture_file else ROOT / "fixtures" / f"{args.fixture}.yaml"
    answers = yaml.safe_load(path.read_text())
    spec = yaml.safe_load((ROOT / "templates" / "variables.yaml").read_text())
    sys.stdout.write(render((ROOT / "templates" / "project-instructions.md").read_text(), answers, spec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
