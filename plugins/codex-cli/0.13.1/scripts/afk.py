#!/usr/bin/env python3
"""afk.py — S-83..S-85: away mode. Decides queue-vs-do, and keeps a Claude Code session on the same thread.

PURPOSE
-------
`classify "<action>"`  S-83: print {"decision": "queue"|"do", "kind", "why"} for an action description
Claude Code hooks (stdin JSON in, hook JSON out), wired in hooks/hooks.json:
  precompact     PreCompact: refresh HANDOVER.md "Next" from the AFK queue (stdout stays empty)
  session-start  SessionStart(compact): inject the HANDOVER state as hookSpecificOutput.additionalContext
  stop           Stop: while AFK is on and runnable work remains, {"decision": "block", "reason": <next task>}
  prompt         UserPromptSubmit: a message STARTING with a trigger phrase turns AFK on for this session; any other message from the owner turns it off
Hook formats: https://code.claude.com/docs/en/hooks.md (read 2026-10-30): PreCompact input has
`trigger` and `custom_instructions`; Stop input has `stop_hook_active`, true while Claude Code is
already continuing because of a stop hook; Stop output `decision: "block"` needs `reason`.

HANDOVER.md shape this reads and writes (the template in cypher-handover, plus):
  AFK: on since <ISO time>          (or `AFK: off since <ISO time>`; the last such line wins)
  AFK token cap: <n>                (optional)
  Next (exact first action): <...>
  ## AFK queue                      `- [ ]` runnable, `- [x]` done, `- [?]` waits on the owner
  ## Morning report queue           `- <gate|restart|destroy|downtime>: <what>`

CONVENTIONS
-----------
- Everything above `main` is pure (text in, text or dict out). Files, the clock, env and stdio are at the edge.
- Fail open: bad input, a missing file or an unreadable state file prints `afk: ...` on stderr and allows
  (the Stop hook never traps a session). The cap and the no-progress check are the loop guards, on top of
  Claude Code's own 8-continuation limit.
- Which HANDOVER.md: $CYPHER_AFK_HANDOVER, else the newest ~/scratch/*/HANDOVER.md (or ./HANDOVER.md)
  whose last AFK line is `on`. Two AFK sessions at once need the env var to tell them apart.
- Whose AFK: the AFK line carries the owning session (`AFK: on since <t> session <id>`), found by
  `session <id>` anywhere on the line. A message that STARTS with a trigger phrase ("going to bed",
  "going afk", "afk", "I'm away", /cypher-admin afk) and finds an AFK line writes it as on, owned by that
  session_id, now. Any other message in the owning session turns it off; a message in another session
  changes nothing. First run (no HANDOVER.md or no AFK line yet): the trigger records the session in
  `<state dir>/afk/pending-<session_id>.json` (id sanitised to [A-Za-z0-9_-], 0600); the first
  Stop/PreCompact in that session that finds an `AFK: on` line without a session and its own file
  under 24 h old adds ` session <id>` and deletes the file (an older one is deleted unused). No other session claims,
  and each hook acts only for the owner. The read-modify-write holds an exclusive flock on a sidecar
  `.lock` file and replaces via temp file + rename.
- Token use is billable input + output + cache-creation tokens summed from the transcript; cache reads
  are left out. It is an approximation of the per-session cap, not a meter.

AGENT NOTES
-----------
- Stdlib only. Which services are public comes from the gateway `knowledge` tool at run time and is
  passed in as `public_services`; this file names none.
- The hook never starts a session and never schedules anything.
"""
import calendar
import fcntl
import glob
import hashlib
import json
import os
import pathlib
import re
import sys
import threading
import time

DEFAULT_TOKEN_CAP = 1_500_000
AFK_LINE = re.compile(r"^AFK:\s*(on|off)\b", re.IGNORECASE)
SINCE_TOKEN = re.compile(r"\bsince\s+(\S+)", re.IGNORECASE)
SESSION_TOKEN = re.compile(r"\s*\bsession\s+\S+", re.IGNORECASE)
SESSION_VALUE = re.compile(r"\bsession\s+(\S+)", re.IGNORECASE)
TRIGGER = re.compile(
    r"(?:going to bed\b|going afk\b"
    # bare `afk` is the whole first clause: end, punctuation run, `-ing`, or a short time/leave word
    r"|afk(?:-ing\b|[\"'`\u201c\u201d\u2018\u2019]?\s*$"
    r"|[.!\u2026]+[\"'`\u201c\u201d\u2018\u2019]?(?=$|\s)"
    r"|\s{0,8}[,;\-\u2014]?\s{1,8}(?:now|for|back|til|till|until|bbl|brb|see|night|gn)\b)"
    r"|i(?:'|\u2019)?m away\b|i am away\b|/cypher-admin[ \t]{1,8}afk\b)",
    re.IGNORECASE)
LEAD_NOISE = re.compile(r"^[\s\"'`\u201c\u201d\u2018\u2019>]+")
LEAD_FILLER = re.compile(r"^(?:ok|okay|right|so|well)\b[,\s]*", re.IGNORECASE)
WHITESPACE_RUN = re.compile(r"\s+")
TRIGGER_SCAN_CHARS = 200
PENDING_MAX_AGE = 24 * 3600
CAP_LINE = re.compile(r"^AFK token cap:\s*(\d+)", re.IGNORECASE)
NEXT_LINE = re.compile(r"^Next(?: \(exact first action\))?:\s*(.*)$")
TASK_LINE = re.compile(r"^-\s*\[( |x|\?)\]\s*(.*\S)\s*$")
H2 = re.compile(r"^##\s+(.*?)\s*$")
QUEUE_H = "AFK queue"
MORNING_H = "Morning report queue"

GATE = re.compile(r"\bgate\b|\bUAT\b|\bask (?:the )?owner\b|\bowner (?:to )?(?:approve|answer|decide)\b", re.I)
DESTROY = re.compile(r"\b(?:kill|terminate|destroy|delete|drop|wipe|purge)\b|\brm\s+-rf?\b", re.I)
DOWNTIME = re.compile(r"\bdowntime\b|\bmaintenance window\b|\boutage\b", re.I)
RESTART = re.compile(r"\b(?:restart|reboot|redeploy|bounce|recreate|reload)\b", re.I)
PUBLIC = re.compile(r"\bpublic\b", re.I)


# ---- pure core -------------------------------------------------------------------------

def classify_action(text, public_services=()):
    """S-83: queue (never ask, never do) a gate or a B-lane ask-first action; do the rest."""
    if GATE.search(text):
        return {"decision": "queue", "kind": "gate", "why": "a gate waits on the owner"}
    if DESTROY.search(text):
        return {"decision": "queue", "kind": "destroy", "why": "kill/destroy/delete is ask-first"}
    if DOWNTIME.search(text):
        return {"decision": "queue", "kind": "downtime", "why": "a downtime window is ask-first"}
    if RESTART.search(text):
        low = text.lower()
        if PUBLIC.search(text) or any(s and s.lower() in low for s in public_services):
            return {"decision": "queue", "kind": "restart", "why": "restarting a public service is ask-first"}
    return {"decision": "do", "kind": "", "why": "not a gate or an ask-first action"}


def _section_bounds(lines, heading):
    start = None
    for i, line in enumerate(lines):
        m = H2.match(line)
        if m and m.group(1).lower() == heading.lower():
            start = i
        elif m and start is not None:
            return start, i
    return (start, len(lines)) if start is not None else (None, None)


def parse_handover(text):
    lines = text.splitlines()
    state = {"afk_on": False, "since": "", "session": "", "next": "", "runnable": [], "blocked": [], "done": [], "morning": []}
    for line in lines:
        m = AFK_LINE.match(line)
        if m:
            state["afk_on"] = m.group(1).lower() == "on"
            since, owner = SINCE_TOKEN.search(line), SESSION_VALUE.search(line)
            state["since"] = since.group(1) if since else ""
            state["session"] = owner.group(1) if owner else ""
        m = NEXT_LINE.match(line)
        if m:
            state["next"] = m.group(1).strip()
    s, e = _section_bounds(lines, QUEUE_H)
    for line in (lines[s + 1:e] if s is not None else []):
        m = TASK_LINE.match(line)
        if m:
            key = {" ": "runnable", "x": "done", "?": "blocked"}[m.group(1)]
            state[key].append(m.group(2))
    s, e = _section_bounds(lines, MORNING_H)
    for line in (lines[s + 1:e] if s is not None else []):
        if line.startswith("- "):
            state["morning"].append(line[2:].strip())
    return state


def token_cap(text, env_value=None):
    for line in text.splitlines():
        m = CAP_LINE.match(line)
        if m:
            return int(m.group(1))
    if env_value and str(env_value).isdigit():
        return int(env_value)
    return DEFAULT_TOKEN_CAP


def tokens_used(transcript_lines):
    """Billable tokens, each assistant message counted once: a message that spans several transcript
    lines repeats its id and usage, so the last usage seen for an id is the one that counts."""
    by_id = {}
    for n, raw in enumerate(transcript_lines):
        try:
            msg = json.loads(raw).get("message", {})
            u = msg.get("usage")
        except (ValueError, AttributeError):
            continue
        if isinstance(u, dict):
            by_id[msg.get("id") or f"line-{n}"] = sum(
                int(u.get(k) or 0) for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens"))
    return sum(by_id.values())


def is_afk_trigger(prompt):
    """True when the message STARTS with a cypher-afk trigger phrase; the same words inside a sentence do not count."""
    text = LEAD_NOISE.sub("", prompt or "")
    text = LEAD_NOISE.sub("", LEAD_FILLER.sub("", text))
    text = WHITESPACE_RUN.sub(" ", text[:TRIGGER_SCAN_CHARS * 8])[:TRIGGER_SCAN_CHARS]
    return bool(TRIGGER.match(text))


def pending_is_stale(since, now_epoch):
    """True when a pending record's `since` (UTC, _now() format) is over 24 h old; unreadable counts as stale."""
    try:
        t = calendar.timegm(time.strptime(since, "%Y-%m-%dT%H:%MZ"))
    except (TypeError, ValueError):
        return True
    return now_epoch - t > PENDING_MAX_AGE


def claim_text(text, session):
    """Add ` session <id>` to the last AFK line when it is on and has no owner; otherwise return text unchanged."""
    lines = text.splitlines()
    idx = [i for i, x in enumerate(lines) if AFK_LINE.match(x)]
    if not session or not idx:
        return text
    last = lines[idx[-1]]
    if AFK_LINE.match(last).group(1).lower() != "on" or SESSION_VALUE.search(last):
        return text
    lines[idx[-1]] = f"{last.rstrip()} session {session}"
    return "\n".join(lines) + "\n"


def afk_on_line(session, when):
    return f"AFK: on since {when} session {session}"


def set_afk_on(text, session, when):
    """Write the AFK line as on, owned by `session`, replacing any earlier AFK line (and its session token)."""
    line = afk_on_line(session, when)
    lines = text.splitlines()
    idx = [i for i, x in enumerate(lines) if AFK_LINE.match(x)]
    if idx:
        lines[idx[-1]] = line
        for i in reversed(idx[:-1]):
            del lines[i]
    else:
        lines.insert(1 if lines and lines[0].startswith("#") else 0, line)
    return "\n".join(lines) + "\n"


def prompt_update(text, session, prompt, when):
    """UserPromptSubmit: the trigger words claim AFK for this session; any other message from the
    owning session turns it off; a message in another session changes nothing."""
    if not session:
        return text
    if is_afk_trigger(prompt):
        return set_afk_on(text, session, when)
    state = parse_handover(text)
    if state["afk_on"] and state["session"] == session:
        return turn_off(text, when)
    return text


def next_action_text(state):
    if state["runnable"]:
        return state["runnable"][0]
    return "nothing runnable is left: finish the morning report (cypher-afk section 5) and stop"


def refresh_next(text):
    """PreCompact: set the HANDOVER "Next" line from the queue (insert it when absent)."""
    line = "Next (exact first action): " + next_action_text(parse_handover(text))
    lines = text.splitlines()
    for i, old in enumerate(lines):
        if NEXT_LINE.match(old):
            lines[i] = line
            return "\n".join(lines) + "\n"
    s, _ = _section_bounds(lines, QUEUE_H)
    at = s if s is not None else len(lines)
    lines[at:at] = [line] + ([""] if s is not None else [])
    return "\n".join(lines) + "\n"


def session_start_output(text):
    """SessionStart(compact): the AFK state as additionalContext, or None when AFK is off."""
    s = parse_handover(text)
    if not s["afk_on"]:
        return None
    ctx = [f"AFK mode is on since {s['since'] or 'an earlier time'}. Nothing waits on the owner: gates and ask-first actions go to the morning report queue.",
           "HANDOVER Next: " + (s["next"] or next_action_text(s)),
           "Runnable queue: " + ("; ".join(s["runnable"]) or "empty"),
           f"Queued for the owner: {len(s['morning'])} item(s) in the morning report queue."]
    return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(ctx)}}


def add_to_morning_queue(text, kind, desc):
    item = f"{kind}: {desc}"
    if item in parse_handover(text)["morning"]:
        return text
    lines = text.rstrip("\n").splitlines()
    s, e = _section_bounds(lines, MORNING_H)
    if s is None:
        lines += ["", "## " + MORNING_H, "- " + item]
    else:
        end = e
        while end > s + 1 and not lines[end - 1].strip():
            end -= 1
        lines.insert(end, "- " + item)
    return "\n".join(lines) + "\n"


def turn_off(text, when):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if AFK_LINE.match(line):
            lines[i] = f"AFK: off since {when}"
    return "\n".join(lines) + "\n"


def fingerprint(state):
    return hashlib.sha256((next_action_text(state) + "|" + str(len(state["done"]))).encode()).hexdigest()[:16]


def stop_decision(state, stop_hook_active, tokens_used, cap, last_fingerprint=None):
    """S-85: block with the next task, or None to let the session stop.

    Allow when AFK is off, nothing runnable remains (empty, or only owner-blocked items), the cap is
    reached, or Claude Code is already continuing from a stop hook and the queue has not moved since
    the last block (a loop)."""
    if not state["afk_on"] or not state["runnable"] or tokens_used >= cap:
        return None
    if stop_hook_active and last_fingerprint == fingerprint(state):
        return None
    return {"decision": "block",
            "reason": f"AFK is on and {len(state['runnable'])} task(s) remain. Next: {state['runnable'][0]}. "
                      "Do it, tick it off in the HANDOVER AFK queue, then continue with the next."}


# ---- edge ------------------------------------------------------------------------------

def _state_dir():
    base = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(
        os.environ.get("XDG_STATE_HOME") or os.path.expanduser("~/.local/state"), "cypher-plugin")
    return pathlib.Path(base)


def _pending_file(session):
    return _state_dir() / "afk" / f"pending-{re.sub(r'[^A-Za-z0-9_-]', '_', session)}.json"


def _has_pending(session):
    """True when this session's own pending file is fresh; a stale (>24 h) or unreadable one is deleted."""
    try:
        rec = json.loads(_pending_file(session).read_text())
        since = rec.get("since")
        owner = rec.get("session_id")
    except (OSError, ValueError, AttributeError):
        return False
    if owner != session or pending_is_stale(since, time.time()):
        _clear_pending(session)
        return False
    return True


def _write_pending(session, when):
    """Record the trigger session as the first-run owner: 0600, temp file + rename."""
    f = _pending_file(session)
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_name(f".{f.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(json.dumps({"session_id": session, "since": when}))
    os.replace(tmp, f)


def _clear_pending(session):
    try:
        _pending_file(session).unlink()
    except OSError:
        pass


def find_handover(include_off=False):
    """The HANDOVER.md to act on; include_off also accepts the newest one with an AFK line that is off."""
    env = os.environ.get("CYPHER_AFK_HANDOVER")
    if env:
        return pathlib.Path(env)
    cands = glob.glob(os.path.expanduser("~/scratch/*/HANDOVER.md")) + ["HANDOVER.md"]
    live = []
    for c in cands:
        try:
            text = pathlib.Path(c).read_text()
            if parse_handover(text)["afk_on"]:
                live.append((1, os.path.getmtime(c), c))
            elif include_off and any(AFK_LINE.match(x) for x in text.splitlines()):
                live.append((0, os.path.getmtime(c), c))
        except OSError:
            continue
    return pathlib.Path(max(live)[2]) if live else None


def _fp_file(session):
    return _state_dir() / f"afk-{re.sub(r'[^A-Za-z0-9_.-]', '_', session or 'none')}.json"


def _read_fp(session):
    try:
        return json.loads(_fp_file(session).read_text()).get("fingerprint")
    except (OSError, ValueError):
        return None


def _write_fp(session, fp):
    f = _fp_file(session)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"fingerprint": fp}))


def _now():
    return time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())


def _emit(out, obj):
    if obj:
        out.write(json.dumps(obj))


def locked_update(path, fn):
    """Read-modify-write `path` under an exclusive flock on a sidecar file; replace via temp file + rename."""
    path = pathlib.Path(path)
    with open(path.with_name(path.name + ".lock"), "a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        text = path.read_text()
        new = fn(text)
        if new != text:
            tmp = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
            tmp.write_text(new)
            os.replace(tmp, path)


def hook(cmd, event, out):
    session = event.get("session_id", "")
    if cmd == "prompt":
        if not session:
            return
        prompt = event.get("prompt", "")
        trigger = is_afk_trigger(prompt)
        path = find_handover(include_off=trigger)
        has_line = False
        if path and path.is_file():
            has_line = any(AFK_LINE.match(x) for x in path.read_text().splitlines())
            if has_line or not trigger:
                locked_update(path, lambda t: prompt_update(t, session, prompt, _now()))
        if trigger:
            if has_line:
                _clear_pending(session)
            else:
                _write_pending(session, _now())  # first run: the Stop/PreCompact in this session claims it
        return
    path = find_handover()
    if not path or not path.is_file():
        return
    text = path.read_text()
    state = parse_handover(text)
    if state["afk_on"] and not state["session"] and cmd in ("stop", "precompact") and session \
            and _has_pending(session):
        locked_update(path, lambda t: claim_text(t, session))
        _clear_pending(session)
        text = path.read_text()
        state = parse_handover(text)
    if not state["afk_on"] or not session or state["session"] != session:
        return  # AFK off, unowned, or another session's: only a trigger prompt ever claims
    if cmd == "precompact":
        locked_update(path, refresh_next)
    elif cmd == "session-start":
        if event.get("source") == "compact":
            _emit(out, session_start_output(text))
    elif cmd == "stop":
        used = 0
        tp = event.get("transcript_path")
        if tp and os.path.isfile(tp):
            with open(tp, errors="replace") as fh:
                used = tokens_used(fh)
        d = stop_decision(state, bool(event.get("stop_hook_active")), used,
                          token_cap(text, os.environ.get("CYPHER_AFK_TOKEN_CAP")), _read_fp(session))
        if d:
            _write_fp(session, fingerprint(state))
        _emit(out, d)


def main(argv, stdin, stdout):
    cmd = argv[0] if argv else ""
    if cmd == "classify":
        stdout.write(json.dumps(classify_action(" ".join(argv[1:]), os.environ.get("CYPHER_PUBLIC_SERVICES", "").split(","))) + "\n")
        return 0
    if cmd not in ("precompact", "session-start", "stop", "prompt"):
        sys.stderr.write("afk: usage: afk.py classify <text> | precompact | session-start | stop | prompt\n")
        return 2
    try:
        hook(cmd, json.loads(stdin.read() or "{}"), stdout)
    except Exception as e:  # fail open: a hook bug must never trap or block a session
        sys.stderr.write(f"afk: {cmd} hook skipped: {e}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], sys.stdin, sys.stdout))
