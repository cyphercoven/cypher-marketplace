#!/usr/bin/env python3
"""Check the cypher-legal skill, its eleven area references and their live locator provenance.

PURPOSE: enforce approved area names, source/currency rules and evidence links.
CONVENTIONS: structural validation does not prove legal accuracy or model routing. The shared
rules live once in skills/cypher-legal/SKILL.md; each reference keeps its own locator, conflicts
and signpost. verification.json keeps its historical `law-<area>` keys as provenance.
AGENT NOTES: --verified checks saved live-call evidence; current law still needs rechecking.
"""
import argparse
import json
from pathlib import Path
import re

NAMES = ("research", "education", "family", "housing", "benefits", "employment",
         "criminal", "substances", "corporate", "small-business", "fraud-aml")
HOME = "skills/cypher-legal"
SHARED = ("## Source and currency rules", "## Legal information, not legal advice")
PER_AREA = ("## Known conflicts and reform checks", "## Free advice signpost", "## Starting lookup")


def check(root, verified=False):
    errors = []
    home = root / HOME
    stale = sorted(p.name for p in (root / "skills").glob("law-*") if p.is_dir())
    if stale:
        errors.append("law-* skills must be references of cypher-legal: " + ", ".join(stale))
    actual = {p.stem for p in (home / "references").glob("*.md")}
    if actual != set(NAMES):
        errors.append("reference set differs from approved eleven areas")
    skill = (home / "SKILL.md").read_text()
    for required in SHARED:
        if required not in skill:
            errors.append("cypher-legal: missing " + required)
    if "in_force_verified:false" not in skill or "version date is not commencement proof" not in skill:
        errors.append("cypher-legal: missing explicit currency limit")
    for name in NAMES:
        if "| `%s` | `references/%s.md` |" % (name, name) not in skill:
            errors.append("cypher-legal: no routing row for " + name)
    expected = {"law-" + name for name in NAMES}
    evidence = json.loads((home / "verification.json").read_text()) if verified else []
    by_skill = {e["skill"]: e for e in evidence}
    if verified and (set(by_skill) != expected or len(evidence) != len(expected)):
        errors.append("live evidence must cover each law area exactly once")
    for name in sorted(actual & set(NAMES)):
        text = (home / "references" / (name + ".md")).read_text()
        for required in PER_AREA:
            if required not in text:
                errors.append(name + ": missing " + required)
        if verified:
            row = by_skill.get("law-" + name)
            locator = re.search(r"`ukpga/(\d+)/(\d+)` section `([^\`]+)`", text)
            if not row or not locator:
                errors.append(name + ": locator evidence missing")
                continue
            args, result = row["args"], row["result"]
            found = (int(locator[1]), int(locator[2]), locator[3])
            if found != (args["year"], args["number"], args["section"]):
                errors.append(name + ": locator does not match live call")
            url = "https://www.legislation.gov.uk/ukpga/%s/%s/section/%s" % found
            if row["call"] != "law_legislation_get_section" or result["source_url"] != url:
                errors.append(name + ": wrong source/call")
            if not result["title"] or result["title"] not in text or not row["checked"]:
                errors.append(name + ": missing live result/date")
            if result["content_truncated"]:
                errors.append(name + ": incomplete evidence")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verified", action="store_true")
    args = parser.parse_args()
    failures = check(Path(__file__).resolve().parents[1], args.verified)
    for failure in failures:
        print("FAIL", failure)
    print("law-skills:", "FAIL" if failures else "ok (structural/provenance only)")
    raise SystemExit(bool(failures))
