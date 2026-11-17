#!/usr/bin/env python3
"""PURPOSE: one durable improve checkpoint and cumulative delta resolver for all adapters.
CONVENTIONS: pure scope/assessment functions; Git, state, measured commands and CLI at edge.
AGENT NOTES: runtime artifacts stay outside Git. Claude hooks cover mediated transitions only;
native Codex/local commands need an explicit guarded adapter. No models launch from hooks.
"""
import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

POLICY = "poc-first-v1"
PHASES = ("epic-planning", "plan", "refinement", "feature-review", "production-admission")
REVIEW_PHASES = {"feature-review", "production-admission"}
REVIEW_SEMANTICS = 3  # Complete packets, flat ancestry and immutable state binding.
SYSTEM_PHASES = {"epic-planning", "production-admission"}
RISK_PATTERNS = {
    "identity/isolation": r"auth|identity|permission|tenant|isolation",
    "secrets/sensitive-data": r"secret|credential|vault|sensitive",
    "untrusted-input": r"parser|deserialize|untrusted|exec",
    "data/privilege/exposure": r"migrat|privileg|ingress|firewall",
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def matches(path, patterns):
    return any(fnmatch.fnmatchcase(path, pattern) or
               (pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:]))
               for pattern in patterns)


def safe_pattern(value):
    return (isinstance(value, str) and bool(value) and not value.startswith(("/", "\\"))
            and not re.match(r"^[A-Za-z]:", value) and ".." not in value.replace("\\", "/").split("/"))


def expand_impact(changed, files, dependencies, leaves, broadening):
    """Resolve transitive reverse-dependants; unknown reach needs explicit bounded expansion."""
    impacted, unknown = set(changed), set()
    todo = list(changed)
    while todo:
        path = todo.pop()
        rows = [targets for source, targets in dependencies.items() if matches(path, [source])]
        if not rows and not matches(path, leaves):
            unknown.add(path)
        for targets in rows:
            found = {f for f in files if matches(f, targets)}
            for f in found - impacted:
                impacted.add(f)
                todo.append(f)
    reason = ""
    missing = []
    if unknown:
        reason = str(broadening.get("reason", "")).strip()
        patterns = broadening.get("paths", [])
        if not reason or not patterns or not all(matches(f, patterns) for f in unknown):
            missing.append("Unknown impact: " + ", ".join(sorted(unknown)) +
                           "; declare dependants/leaf paths or reasoned broader scope.")
        else:
            impacted.update(f for f in files if matches(f, patterns))
    return sorted(impacted), missing, reason


def check_inputs(check, files, dependencies):
    """A consumer check depends on its source ancestors, not just its own matched files."""
    selected = {f for f in files if matches(f, check["paths"])}
    changed = True
    while changed:
        before = len(selected)
        for source, targets in dependencies.items():
            if any(matches(f, targets) for f in selected):
                selected.update(f for f in files if matches(f, [source]))
        changed = len(selected) != before
    return {f: files[f] for f in sorted(selected)}


def check_phases(check):
    return check.get("phases", ["epic-planning", "feature-review", "production-admission"]
                     if check.get("kind") == "security" else ["feature-review", "production-admission"])


def criteria_errors(criteria):
    if not isinstance(criteria, list) or not criteria:
        return ["A self-contained nonempty acceptance packet is required."]
    ids = set()
    for item in criteria:
        if (not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip()
                or item["id"] in ids or not isinstance(item.get("criterion"), str) or not item["criterion"].strip()):
            return ["Acceptance criteria need unique IDs and explicit criterion text."]
        ids.add(item["id"])
        if item.get("phase", "poc") not in {"poc", "refinement", "production"}:
            return ["Acceptance phase must be poc, refinement or production."]
        if not all(safe_pattern(p) for p in item.get("paths", [])):
            return ["Acceptance paths must be relative nontraversing patterns."]
    return []


def result_errors(result, request, context):
    errors = []
    if result.get("schema_version") != 1 or result.get("outcome") != "pass":
        errors.append("Result requires schema_version 1 and outcome pass.")
    if result.get("request_digest") != request["request_digest"]:
        errors.append("Result is stale or does not identify this resolved request.")
    if not isinstance(result.get("summary"), str) or not result["summary"].strip():
        errors.append("Result needs a substantive summary.")
    assessment = result.get("assessment", {})
    if not isinstance(assessment, dict):
        return errors + ["Assessment must be an object."]
    for key in ("risks", "security") + (("systems_fit",) if request["phase"] in SYSTEM_PHASES else ()):
        if not isinstance(assessment.get(key), str) or not assessment[key].strip():
            errors.append("Missing assessment: " + key)
    if request["phase"] in REVIEW_PHASES:
        reviewer = result.get("reviewer")
        if not isinstance(reviewer, str) or not reviewer.strip() or reviewer.strip().casefold() == context["implementer"].strip().casefold():
            errors.append("Independent reviewer must be named and differ from implementer.")
        coverage = result.get("reviewed_paths", [])
        if not isinstance(coverage, list) or not all(isinstance(x, str) for x in coverage) or not set(request["impacted_paths"]).issubset(coverage):
            errors.append("Review does not cover resolved impacted paths.")
    if request["phase"] in REVIEW_PHASES:
        outcomes = result.get("criteria", [])
        if not isinstance(outcomes, list):
            outcomes = []
        proven = {item.get("id") for item in outcomes if isinstance(item, dict)
                  and item.get("outcome") == "pass" and isinstance(item.get("evidence"), str)
                  and item["evidence"].strip()}
        if not {item["id"] for item in request["acceptance"]}.issubset(proven):
            errors.append("Missing passing observations for requested acceptance criteria.")
        if request["phase"] == "production-admission" and not assessment.get("full_spec_fit"):
            errors.append("Final admission requires full-spec fit assessment.")
    findings = result.get("findings")
    if not isinstance(findings, list):
        errors.append("Findings must be a list, including when empty.")
    else:
        for finding in findings:
            if not isinstance(finding, dict):
                errors.append("Malformed finding.")
                continue
            unresolved = finding.get("status") != "resolved"
            category = finding.get("category")
            if category not in {"security", "journey", "other"} or finding.get("severity") not in {"P0", "P1", "P2", "P3"}:
                errors.append("Finding needs category and severity.")
            if unresolved and (category in {"security", "journey"} or
                               (request["phase"] == "production-admission" and finding.get("severity") in {"P0", "P1", "P2"})):
                errors.append("Blocking finding remains unresolved.")
            if unresolved and not all(finding.get(k) for k in ("owner", "evidence")):
                errors.append("Deferred finding needs ownership and evidence.")
    return errors


def file_hash(path):
    path = Path(path)
    if path.is_symlink():
        return digest({"symlink": os.readlink(path)})
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as stream:
        json.dump(value, stream, sort_keys=True)
        temporary = stream.name
    os.replace(temporary, path)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True, timeout=20).stdout


def pattern_contained(child, parent):
    """Prove inclusion without treating a child glob as a candidate filename."""
    if child == parent or parent == "**":
        return True
    if not any(c in child for c in "*?["):
        return matches(child, [parent])
    if parent.endswith("/**") and not any(c in parent[:-3] for c in "*?["):
        prefix = parent[:-3] + "/"
        return child.startswith(prefix)
    return False


def scope_patterns(context):
    patterns = list(context["paths"]) + list(context["leaf_paths"]) + list(context["dependencies"])
    patterns += context["broadening"].get("paths", [])
    for targets in context["dependencies"].values():
        patterns += targets
    for check in context["checks"]:
        patterns += check["paths"]
    for criterion in context["acceptance"]:
        patterns += criterion.get("paths", [])
    return patterns


def load_context(path, linked=False):
    context = read_json(path)
    if not isinstance(context, dict):
        raise ValueError("Context must be a JSON object.")
    if linked and "epic_context" in context:
        raise ValueError("epic_context must be one hop; self, cyclic and nested links are forbidden.")
    if context.get("schema_version") != 1 or context.get("policy") != POLICY:
        raise ValueError("Unsupported context schema/policy.")
    for key in ("run", "scope", "repo", "base", "plan", "state_dir", "implementer"):
        if not isinstance(context.get(key), str) or not context[key].strip():
            raise ValueError("Missing context field: " + key)
    repo = Path(context["repo"]).resolve()
    if Path(git(repo, "rev-parse", "--show-toplevel").strip()).resolve() != repo:
        raise ValueError("repo must name its Git top level.")
    state = Path(context["state_dir"]).resolve()
    if state == repo or repo in state.parents:
        raise ValueError("Runtime state_dir must be outside the repository.")
    if not Path(context["plan"]).is_file() or not Path(context["plan"]).read_text().strip():
        raise ValueError("Plan artifact is missing or empty.")
    problems = criteria_errors(context.get("acceptance"))
    if problems:
        raise ValueError(problems[0])
    if "admission_required" in context and not isinstance(context["admission_required"], bool):
        raise ValueError("admission_required must be a boolean.")
    context.setdefault("planning_inputs", [])
    context.setdefault("paths", [])
    context.setdefault("dependencies", {})
    context.setdefault("leaf_paths", [])
    context.setdefault("checks", [])
    context.setdefault("config_paths", [])
    context.setdefault("external_state_paths", [])
    context.setdefault("broadening", {})
    if not context["paths"] or not isinstance(context["dependencies"], dict):
        raise ValueError("Declare paths and a dependency map.")
    patterns = list(context["paths"]) + list(context["leaf_paths"]) + list(context["dependencies"])
    patterns += context["broadening"].get("paths", [])
    for targets in context["dependencies"].values():
        if not isinstance(targets, list) or not targets:
            raise ValueError("Dependency targets must be nonempty pattern lists; use leaf_paths for leaves.")
        patterns += targets
    ids = set()
    for check in context["checks"]:
        if not isinstance(check.get("id"), str) or check["id"] in ids:
            raise ValueError("Checks need unique string IDs.")
        ids.add(check["id"])
        if not check.get("paths") or not check.get("argv") or not all(isinstance(x, str) for x in check["argv"]):
            raise ValueError("Check requires paths and an argv string list.")
        patterns += check["paths"]
        if "config_paths" in check:
            selected = check["config_paths"]
            declared = context["config_paths"]
            if (not isinstance(selected, list) or not selected or
                    not isinstance(declared, list) or not all(isinstance(p, str) for p in declared)):
                raise ValueError("Check config_paths requires a nonempty admitted file list.")
            admitted = {str(Path(p).resolve()) for p in declared}
            for entry in selected:
                if (not isinstance(entry, str) or not Path(entry).is_absolute() or
                        Path(entry).is_symlink() or not Path(entry).is_file() or
                        str(Path(entry).resolve()) not in admitted):
                    raise ValueError("Check config_paths must select admitted absolute regular files, not symlinks.")
            check["config_paths"] = sorted({str(Path(p).resolve()) for p in selected})
        if not all(p in PHASES for p in check_phases(check)):
            raise ValueError("Check phases must name supported lifecycle checkpoints.")
        if check.get("breadth") == "whole-suite" and not context["broadening"].get("reason"):
            raise ValueError("Whole-suite checks require an explicit recorded broadening reason.")
    if not all(safe_pattern(p) for p in patterns):
        raise ValueError("Scope paths must be relative, nontraversing patterns.")
    # Resolve the base now, not through shell interpolation later.
    context["base"] = git(repo, "rev-parse", "--verify", context["base"] + "^{commit}").strip()
    context["repo"] = str(repo)
    context["state_dir"] = str(state)
    if "epic_context" in context:
        link = context["epic_context"]
        if not isinstance(link, str) or not Path(link).is_absolute():
            raise ValueError("epic_context must name an absolute stable context path.")
        if Path(link).resolve() == Path(path).resolve():
            raise ValueError("epic_context cannot link to itself.")
        parent = load_context(link, linked=True)
        if parent["repo"] != context["repo"] or parent["run"] != context["run"]:
            raise ValueError("epic_context must use the same resolved Git top-level repo and run.")
        if parent["scope"] != "epic" or context["scope"] == parent["scope"]:
            raise ValueError("epic_context needs a stable epic scope distinct from the job scope.")
        for pattern in scope_patterns(context):
            if not any(pattern_contained(pattern, upper) for upper in parent["paths"]):
                raise ValueError("epic_context scope inclusion is unproven for " + pattern +
                                 "; repair with a contained literal or supported directory/** pattern.")
        context["epic_context"] = str(Path(link).resolve())
    return context


def evidence_dir(context):
    return Path(context["state_dir"]) / digest([context["policy"], context["run"], context["scope"], context["repo"]])


def stored(path):
    return read_json(path) if path.exists() else None


def current_source(context):
    repo = Path(context["repo"])
    paths = set(git(repo, "ls-files", "-z").split("\0"))
    paths.update(git(repo, "ls-files", "--others", "--exclude-standard", "-z").split("\0"))
    snapshot = {}
    for name in sorted(paths - {""}):
        path = repo / name
        if path.is_file() or path.is_symlink():
            snapshot[name] = digest({"content": file_hash(path), "mode": path.lstat().st_mode & 0o777})
        elif path.is_dir():
            raise ValueError("Submodule/directory impact is not bounded: " + name)
    return snapshot


def measured_valid(measurement, fingerprint):
    try:
        return (measurement and measurement["fingerprint"] == fingerprint and measurement["exit_code"] == 0
                and Path(measurement["log"]).is_file() and file_hash(measurement["log"]) == measurement["log_sha256"])
    except (KeyError, OSError, TypeError):
        return False


def owner_poc_inputs(context):
    """Validate recorded owner-chat decisions against stable shown POC packets, not current output."""
    applicability = context.get("applicability", {})
    if (context.get("lane") in {"production-fix", "ops"} and
            all(isinstance(applicability.get(k), str) and applicability[k].strip() for k in ("reason", "reference"))):
        return {}, [], [{"state": "existing-production-path", "reason": applicability["reason"],
                         "reference": applicability["reference"]}]
    prerequisites = context.get("poc_prerequisites", [])
    if not isinstance(prerequisites, list) or not prerequisites:
        return {}, ["Owner POC approval prerequisites are required before refinement/production."], []
    fingerprints, errors, readiness = {}, [], []
    seen = set()
    for poc in prerequisites:
        try:
            if not poc.get("id") or poc["id"] in seen or not poc.get("milestone") or not poc.get("scope"):
                raise ValueError("POC needs unique id, milestone and approved scope.")
            seen.add(poc["id"])
            if criteria_errors(poc.get("acceptance")):
                raise ValueError("POC acceptance packet is missing.")
            demo = poc.get("demo", {})
            if not all(isinstance(demo.get(k), str) and demo[k].strip() for k in ("reference", "revision")):
                raise ValueError("Shown POC demo reference and revision are required.")
            approval = read_json(poc["approval"])
            expected = {"schema_version": 1, "decision": "approved", "poc_id": poc["id"],
                        "milestone": poc["milestone"], "acceptance_digest": digest(poc["acceptance"]),
                        "demo_digest": digest(demo), "scope_digest": digest(poc["scope"])}
            if any(approval.get(k) != v for k, v in expected.items()):
                raise ValueError("Decision is missing, revoked or bound to another shown POC/scope.")
            provenance = approval.get("provenance", {})
            if provenance.get("kind") != "owner-chat" or not all(
                    isinstance(provenance.get(k), str) and provenance[k].strip()
                    for k in ("reference", "quote", "recorded_by")):
                raise ValueError("Explicit owner-chat approval provenance is required; agent/test success is insufficient.")
            fingerprints[poc["id"]] = file_hash(poc["approval"])
            readiness.append({"id": poc["id"], "state": "refinement-ready", "approval": poc["approval"]})
        except (KeyError, OSError, ValueError, TypeError) as exc:
            errors.append("Owner POC approval: " + str(exc))
            readiness.append({"id": poc.get("id") if isinstance(poc, dict) else None, "state": "waiting-owner"})
    return fingerprints, errors, readiness


def check_measurement(directory, ident, fingerprint):
    # A later phase may bind the same check to different inputs. Keep both
    # measurements so refreshing one does not invalidate the other gate.
    cached = directory / ("check-" + digest(ident) + "-" + fingerprint + ".json")
    return stored(cached) if cached.exists() else stored(directory / ("check-" + digest(ident) + ".json"))


def resolve(context, phase):
    if phase == "epic-planning" and context.get("epic_context"):
        raise ValueError("Assess epic-planning explicitly against epic_context: " + context["epic_context"])
    directory = evidence_dir(context)
    previous = stored(directory / (phase + ".json"))
    if phase in REVIEW_PHASES and previous and previous.get("review_semantics") != REVIEW_SEMANTICS:
        previous = None  # Legacy path-filtered evidence must receive a fresh complete review.
    files = current_source(context)
    head = git(context["repo"], "rev-parse", "HEAD").strip()
    if previous:
        before = previous["snapshot"]
        changed = sorted(f for f in set(before) | set(files) if before.get(f) != files.get(f))
    else:
        changed = sorted(set(git(context["repo"], "diff", "--name-only", "-z", context["base"], "--").split("\0")) - {""})
        changed += sorted(set(git(context["repo"], "ls-files", "--others", "--exclude-standard", "-z").split("\0")) - {"", *changed})
    scoped = sorted(f for f in files if matches(f, context["paths"]))
    impacted, missing, reason = expand_impact(changed, set(files) | set(changed),
                                             context["dependencies"], context["leaf_paths"], context["broadening"])
    if previous is None:
        impacted = sorted(set(impacted) | set(scoped))
    outside = [f for f in changed if not matches(f, context["paths"])]
    if outside and not (reason and all(matches(f, context["broadening"]["paths"]) for f in outside)):
        missing.append("Changes outside declared feature scope: " + ", ".join(outside))
    inputs = {str(Path(p).resolve()): file_hash(p)
              for p in context["config_paths"] + context["external_state_paths"] + context["planning_inputs"]}
    common = {"policy": POLICY, "validator_sha256": file_hash(Path(__file__).resolve()),
              "review_semantics": REVIEW_SEMANTICS, "plan": file_hash(context["plan"]), "inputs": inputs,
              "paths": context["paths"], "dependencies": context["dependencies"],
              "leaves": context["leaf_paths"], "broadening": context["broadening"]}
    if phase == "epic-planning":
        common["full_spec_inputs"] = {key: file_hash(value) for key, value in context.get("full_spec", {}).items()
                                     if key == "path"}
    epic = None
    if context.get("epic_context"):
        parent = load_context(context["epic_context"])
        status = checkpoint_status(parent, "epic-planning")
        epic = {"context": context["epic_context"], "repo": parent["repo"], "run": parent["run"],
                "scope": parent["scope"], "identity": digest(parent),
                "request_digest": status["request_digest"]}
        common["epic"] = epic
        if not status["allowed"]:
            missing.append("Missing or stale linked epic-planning; repair explicit epic_context assessment/checks.")
    future_execution = phase in {"plan", "feature-review"} and any(
        item.get("phase", "poc") != "poc" for item in context["acceptance"])
    approvals, approval_errors, readiness = owner_poc_inputs(context) if phase in {"refinement", "production-admission"} or future_execution else ({}, [], [])
    missing.extend(approval_errors)
    acceptance = context["acceptance"]
    full_spec = None
    if phase == "production-admission":
        spec = context.get("full_spec", {})
        if not spec.get("path") or not spec.get("criteria_path"):
            missing.append("Final admission requires full_spec path and complete criteria_path.")
            acceptance = []
        else:
            release_packet = read_json(spec["criteria_path"])
            acceptance = release_packet.get("criteria") if isinstance(release_packet, dict) else release_packet
            missing.extend(criteria_errors(acceptance))
            canonical = re.findall(r"^#{1,6}\s+(S-\d+)\b", Path(spec["path"]).read_text(), re.M)
            if not canonical or len(canonical) != len(set(canonical)):
                missing.append("Full spec must have unique canonical S-NN Markdown headings.")
            elif isinstance(acceptance, list) and all(isinstance(item, dict) for item in acceptance):
                if {item.get("id") for item in acceptance} != set(canonical):
                    missing.append("Release criteria must exactly cover canonical full-spec S-IDs.")
            full_spec = {"path": spec["path"], "sha256": file_hash(spec["path"]),
                         "criteria_path": spec["criteria_path"], "criteria_sha256": file_hash(spec["criteria_path"])}
    # Expected implementation output does not reopen approved planning decisions.
    identity_source = {} if phase in {"epic-planning", "plan", "refinement"} else {
        f: value for f, value in files.items() if matches(f, context["paths"]) or f in impacted}
    identity = {"context": context, "phase": phase, "snapshot": identity_source,
                "common": common, "acceptance": acceptance, "full_spec": full_spec, "owner_approvals": approvals}
    review_context = digest({k: v for k, v in identity.items() if k != "snapshot"})
    if phase in REVIEW_PHASES:
        identity["review_semantics"] = REVIEW_SEMANTICS
    request_id = digest(identity)
    complete_packet = (phase == "production-admission" or not previous or
                       previous.get("review_context_digest") != review_context)
    requested_acceptance = [item for item in acceptance if complete_packet or
                            not item.get("paths") or not impacted or any(matches(f, item["paths"]) for f in impacted)]
    risks = sorted(k for k, pattern in RISK_PATTERNS.items() if any(re.search(pattern, f, re.I) for f in impacted))
    risks = sorted(set(risks) | set(context.get("security_triggers", [])))
    active = [c for c in context["checks"] if phase in check_phases(c)]
    selected = [c for c in active if
                any(matches(f, c["paths"]) for f in impacted) or
                (risks and c.get("kind") == "security")]
    # Input changes can invalidate checks even when no source file changed.
    fingerprints = {}
    for check in context["checks"]:
        checked_common = common
        if "config_paths" in check:
            # Admission owns the declared tool/module closure. Governing state is never optional.
            paths = check["config_paths"] + context["external_state_paths"] + context["planning_inputs"]
            checked_common = {**common, "inputs": {
                str(Path(p).resolve()): inputs[str(Path(p).resolve())] for p in paths}}
        fingerprints[check["id"]] = digest({"common": checked_common, "check": check,
                                            "source": check_inputs(check, files, context["dependencies"])})
    reused, pending = [], []
    for check in active:
        measure = check_measurement(directory, check["id"], fingerprints[check["id"]])
        if measured_valid(measure, fingerprints[check["id"]]):
            reused.append(check["id"])
        elif check in selected or measure:
            pending.append(check["id"])
    if risks and phase in SYSTEM_PHASES | REVIEW_PHASES and not any(c.get("kind") == "security" for c in selected):
        missing.append("Security triggers require a declared focused security check: " + ", ".join(risks))
    if impacted and phase in REVIEW_PHASES and not selected:
        missing.append("No configured check covers the resolved acceptance scope.")
    return {"schema_version": 1, "policy": POLICY, "run": context["run"], "scope": context["scope"],
            "review_dispatch_allowed": False, "epic_provenance": epic,
            "phase": phase, "mode": {"epic-planning": "review-plan", "plan": "plan",
                                    "refinement": "audit-focused", "feature-review": "review",
                                    "production-admission": "review-readiness"}[phase],
            "plan": context["plan"], "action": "Load cypher-improve; resolve missing scope, run pending checks, "
            "then independently assess the current result and record it.",
            "request_digest": request_id, "head": head, "evidence_head": previous.get("head") if previous else None, "snapshot": files,
            "changed_paths": sorted(set(changed)), "impacted_paths": impacted,
            "pending_checks": sorted(pending), "reused_checks": sorted(reused),
            "security_triggers": risks, "broadening_reason": reason, "missing": missing,
            "acceptance": requested_acceptance, "acceptance_packet": acceptance,
            "acceptance_digest": digest(acceptance), "full_spec": full_spec,
            "review_semantics": REVIEW_SEMANTICS, "review_context_digest": review_context,
            "poc_readiness": readiness, "required_phase": "owner-poc-approval" if approval_errors else phase,
            "prior_evidence": [{"artifact": previous["artifact"], "sha256": previous["artifact_sha256"],
                                "request_digest": previous["request_digest"]}] if previous else [],
            "fingerprints": fingerprints}


def checkpoint_status(context, phase, request=None, enforce_admission=True):
    if phase == "epic-planning" and context.get("epic_context"):
        parent = load_context(context["epic_context"])
        status = checkpoint_status(parent, phase)
        return {**status, "review_dispatch_allowed": False, "plan": context["plan"],
                "job_binding": {key: context[key] for key in ("repo", "run", "scope", "plan", "epic_context")},
                "epic_provenance": {"context": context["epic_context"], "repo": parent["repo"],
                                    "run": parent["run"], "scope": parent["scope"],
                                    "plan": parent["plan"],
                                    "request_digest": status["request_digest"]}}
    request = request or resolve(context, phase)
    record = stored(evidence_dir(context) / (phase + ".json"))
    errors = list(request["missing"])
    if request["pending_checks"]:
        errors.append("Missing/invalid measured checks: " + ", ".join(request["pending_checks"]))
    sound = not record or (artifact_chain_valid(record) and
                          (phase not in REVIEW_PHASES or review_coverage_valid(record, record)))
    current = bool(record and record.get("request_digest") == request["request_digest"])
    dispatch_ready = not errors and sound
    if not sound:
        errors.append("Recorded review/result ancestry, state, coverage or measured log changed.")
    if not current:
        errors.append("Missing or stale " + phase + " checkpoint.")
    elif phase in REVIEW_PHASES and not review_coverage_valid(record, request):
        errors.append("Immutable review evidence does not cover the complete current acceptance packet.")
    if phase in {"plan", "refinement"}:
        planning = checkpoint_status(context, "epic-planning")
        if not planning["allowed"]:
            errors.append("Missing or stale epic-planning verification; repair before implementation dispatch.")
    required_phase = request.get("required_phase", phase)
    review_dispatch_allowed = False
    if phase == "feature-review":
        plan = checkpoint_status(context, "plan")
        review_dispatch_allowed = bool(dispatch_ready and not current and plan["allowed"])
    if phase == "feature-review" and enforce_admission and context.get("admission_required"):
        feature_ready = not errors
        final = checkpoint_status(context, "production-admission")
        if not final["allowed"]:
            errors.append("Managed production merge requires current production-admission evidence.")
            if feature_ready:
                required_phase = final.get("required_phase", "production-admission")
    return {**request, "allowed": not errors, "missing": errors, "required_phase": required_phase,
            "review_dispatch_allowed": review_dispatch_allowed}


def run_checks(context, phase):
    request = resolve(context, phase)
    if request["missing"]:
        return {**request, "allowed": False}, 1
    directory = evidence_dir(context)
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / "checks.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return {**request, "allowed": False, "missing": ["Checks already in progress; inspect the existing run."]}, 1
    os.close(fd)
    try:
        for ident in request["pending_checks"]:
            check = next(c for c in context["checks"] if c["id"] == ident)
            log = directory / ("check-" + digest(ident) + "-" + request["fingerprints"][ident] + ".log")
            try:
                completed = subprocess.run(check["argv"], cwd=context["repo"], capture_output=True,
                                           timeout=min(int(check.get("timeout", 120)), 300), check=False)
                payload = completed.stdout + completed.stderr
                code = completed.returncode
            except (OSError, subprocess.TimeoutExpired) as exc:
                payload, code = str(exc).encode(), 124
            log.write_bytes(payload)
            after = resolve(context, phase)
            if request["request_digest"] != after["request_digest"]:
                return {**after, "allowed": False, "missing": ["Source/configuration changed while checks ran."]}, 1
            measurement = {"fingerprint": request["fingerprints"][ident], "argv": check["argv"],
                           "exit_code": code, "log": str(log), "log_sha256": file_hash(log)}
            atomic_json(directory / ("check-" + digest(ident) + "-" + request["fingerprints"][ident] + ".json"), measurement)
            atomic_json(directory / ("check-" + digest(ident) + ".json"), measurement)
            if code:
                return {**request, "allowed": False, "missing": ["Check failed: " + ident], "log": str(log)}, 1
        return {**resolve(context, phase), "allowed": True}, 0
    finally:
        lock.unlink(missing_ok=True)


def artifact_chain_valid(record):
    try:
        for index, item in enumerate([record] + record.get("evidence_chain", [])):
            if file_hash(item["artifact"]) != item["artifact_sha256"]:
                return False
            result = read_json(item["artifact"])
            if result.get("request_digest") != item["request_digest"]:
                return False
            state = result.get("evidence_state")
            if not isinstance(state, dict) or result.get("evidence_binding") != digest(state):
                return False
            if index == 0 and state != {k: v for k, v in item.items()
                    if k not in {"artifact", "artifact_sha256", "submitted_from"}}:
                return False
            if state.get("request_digest") != item["request_digest"]:
                return False
            for measure in state.get("measured_checks", []):
                if not measured_valid(measure, measure["fingerprint"]):
                    return False
        return True
    except (AttributeError, KeyError, OSError, TypeError, ValueError):
        return False


def review_coverage_valid(record, request):
    """Reuse only criterion observations bound inside immutable results to this review context."""
    try:
        covered = set()
        for index, item in enumerate([record] + record.get("evidence_chain", [])):
            result = read_json(item["artifact"])
            metadata = result.get("checkpoint", {})
            if metadata.get("review_semantics") != REVIEW_SEMANTICS:
                return False
            if index == 0 and (metadata.get("review_context_digest") != request["review_context_digest"] or
                               metadata.get("acceptance_digest") != request["acceptance_digest"]):
                return False
            if metadata.get("review_context_digest") != request["review_context_digest"]:
                continue
            acceptance = metadata.get("acceptance")
            if criteria_errors(acceptance):
                return False
            observations = {entry.get("id") for entry in result.get("criteria", [])
                            if isinstance(entry, dict) and entry.get("outcome") == "pass" and
                            isinstance(entry.get("evidence"), str) and entry["evidence"].strip()}
            if not {criterion["id"] for criterion in acceptance}.issubset(observations):
                return False
            covered.update(digest(criterion) for criterion in acceptance)
        return {digest(criterion) for criterion in request["acceptance_packet"]}.issubset(covered)
    except (KeyError, OSError, TypeError, ValueError):
        return False


def record_result(context, phase, path):
    request = resolve(context, phase)
    result = read_json(path)
    errors = request["missing"] + result_errors(result, request, context)
    if request["pending_checks"]:
        errors.append("Run measured checks first: " + ", ".join(request["pending_checks"]))
    if phase == "production-admission":
        feature = checkpoint_status(context, "feature-review", enforce_admission=False)
        if not feature["allowed"]:
            errors.append("Production admission requires a current independent feature review.")
    if errors:
        return {**request, "allowed": False, "missing": errors}, 1
    artifact = Path(path).resolve()
    repo = Path(context["repo"])
    # Result is immutable evidence outside Git; changing it later invalidates the checkpoint.
    if artifact == repo or repo in artifact.parents:
        raise ValueError("Checkpoint result artifacts must stay outside the repository.")
    previous = stored(evidence_dir(context) / (phase + ".json"))
    if previous and previous.get("review_semantics") != REVIEW_SEMANTICS:
        previous = None
    if previous and not artifact_chain_valid(previous):
        return {**request, "allowed": False, "missing": ["Prior evidence ancestry is damaged; restore it before recording a delta."]}, 1
    if phase in REVIEW_PHASES:
        result["checkpoint"] = {key: request[key] for key in
                                ("review_semantics", "review_context_digest", "acceptance_digest", "acceptance")}
    chain = list(previous.get("evidence_chain", [])) if previous else []
    if previous and previous["request_digest"] != request["request_digest"]:
        chain.append({k: previous[k] for k in ("artifact", "artifact_sha256", "request_digest")})
    measures = [check_measurement(evidence_dir(context), c["id"], request["fingerprints"][c["id"]])
                for c in context["checks"] if c["id"] in request["reused_checks"]]
    record = {**request, "evidence_chain": chain, "measured_checks": measures,
              "covered_paths": sorted(set(previous.get("covered_paths", []) if previous else []) |
                                      set(result.get("reviewed_paths", request["impacted_paths"])))}
    result["evidence_binding"] = digest(record)
    result["evidence_state"] = record
    payload = json.dumps(result, sort_keys=True, indent=2).encode()
    content_hash = hashlib.sha256(payload).hexdigest()
    immutable = evidence_dir(context) / "results" / (content_hash + ".json")
    immutable.parent.mkdir(parents=True, exist_ok=True)
    if immutable.exists() and file_hash(immutable) != content_hash:
        raise ValueError("Immutable artifact was modified.")
    immutable.write_bytes(payload)
    record.update(artifact=str(immutable), artifact_sha256=content_hash, submitted_from=str(artifact))
    if phase in REVIEW_PHASES and not review_coverage_valid(record, request):
        return {**request, "allowed": False, "missing": ["Immutable review evidence does not cover the complete current acceptance packet."]}, 1
    if resolve(context, phase)["request_digest"] != request["request_digest"]:
        return {**request, "allowed": False, "missing": ["Inputs changed during admission."]}, 1
    atomic_json(evidence_dir(context) / (phase + ".json"), record)
    return {**request, "allowed": True, "artifact": str(immutable), "covered_paths": record["covered_paths"], "evidence_chain": chain}, 0


def binding_root():
    base = os.environ.get("CLAUDE_PLUGIN_DATA") or str(Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))) / "cypher-plugin")
    return Path(base) / "improve-bindings"


def binding_path(session):
    return binding_root() / (digest(str(session)) + ".json")


def transition_phase(tool, args):
    bare = re.sub(r"^mcp__.+?__", "", tool)
    if tool in {"Task", "Agent"}:
        return None if args.get("subagent_type") in {"Plan", "Explore"} else "plan"
    if bare == "forgejo_pr_merge":
        return "feature-review"
    if bare in {"improve_production_admission", "production_admission"}:
        return "production-admission"
    if tool in {"Bash", "PowerShell"} or bare == "workspace_exec":
        command = str(args.get("command", args.get("cmd", "")))
        if re.search(r"factory/bin/seat\.sh(?:\s|$)", command):
            return "refinement" if os.environ.get("IMPROVE_PHASE") == "refinement" else "plan"
    return None


def hook_decision(event):
    phase = transition_phase(event.get("tool_name", ""), event.get("tool_input") or {})
    if not phase:
        return None
    try:
        context_path = os.environ.get("CYPHER_IMPROVE_CONTEXT")
        if not context_path:
            binding = stored(binding_path(event.get("session_id", "")))
            context_path = binding["context"] if binding else None
        if not context_path:
            return ("Load cypher-improve (Skill tool), create the run context and plan, then bind it with "
                    "improve_checkpoint.py bind --context PATH --session " + str(event.get("session_id", "")) +
                    ". An improve checkpoint is required before this transition; reads and planner repair remain available.")
        context = load_context(context_path)
        if re.sub(r"^mcp__.+?__", "", event.get("tool_name", "")) == "forgejo_pr_merge":
            target = context.get("merge_target", {})
            args = event.get("tool_input") or {}
            if (not isinstance(target, dict) or not isinstance(target.get("repo"), str)
                    or type(target.get("number")) is not int or target["number"] < 1
                    or not isinstance(target.get("head"), str)
                    or args.get("repo") != target.get("repo")
                    or type(args.get("number")) is not int or args["number"] != target["number"]):
                return "Merge target missing or mismatched: bind this context to the exact repo, PR number and declared head."
            if git(context["repo"], "rev-parse", "HEAD").strip() != target["head"]:
                return "Merge target head differs from the reviewed local source; refresh target provenance and affected evidence."
            if git(context["repo"], "status", "--porcelain", "--untracked-files=all").strip():
                return "Merge target source is dirty or has untracked files; commit the reviewed candidate before merging."
        status = checkpoint_status(context, phase)
        if not status["allowed"]:
            return ("Load cypher-improve (Skill tool); " + status["action"] + " "
                    + json.dumps({"phase": phase, "mode": status["mode"], "plan": status["plan"],
                                  "context": context_path, "missing": status["missing"]}))
    except Exception as exc:
        return "Improve checkpoint validation failed closed for this transition: " + type(exc).__name__ + ". Repair context/evidence; reads remain available."
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("resolve", "check", "run-checks", "record", "bind"))
    parser.add_argument("--context", required=True)
    parser.add_argument("--phase", choices=PHASES, default="plan")
    parser.add_argument("--result")
    parser.add_argument("--session")
    args = parser.parse_args(argv)
    try:
        context = load_context(args.context)
        if args.command == "bind":
            if not args.session:
                raise ValueError("bind requires --session.")
            atomic_json(binding_path(args.session), {"context": str(Path(args.context).resolve())})
            output, code = {"allowed": True, "context": args.context, "session": args.session}, 0
        elif args.command == "resolve":
            output, code = resolve(context, args.phase), 0
        elif args.command == "check":
            output = checkpoint_status(context, args.phase)
            code = 0 if output["allowed"] else 1
        elif args.command == "run-checks":
            output, code = run_checks(context, args.phase)
        elif not args.result:
            raise ValueError("record requires --result.")
        else:
            output, code = record_result(context, args.phase, args.result)
        output.setdefault("review_dispatch_allowed", False)
        print(json.dumps(output, sort_keys=True))
        return code
    except Exception as exc:
        print(json.dumps({"allowed": False, "review_dispatch_allowed": False, "error": str(exc),
                          "action": "Repair context/evidence; do not retry in a loop."}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
