---
name: cypher-troubleshoot
user-invocable: false
description: Helps diagnose why something on the Cypher-managed stack looks broken — "what's broken?", "why is X down?", a failing call, an unexpected result — and runs the error-triage routine (read recent error signatures, keep one OPS item per fingerprint, report briefly, fix only on the owner's reply). Use when someone asks what's wrong, what's broken, why something isn't working, or to triage errors, and wants a cause and a next step rather than raw tool output.
---

# cypher-troubleshoot

PURPOSE: answer "what's broken / why is X down" using only what this
person can actually reach and only what the gateway reports right now —
never a guessed host, service, or cause. The same skill is the error-triage
routine: one OPS work item per error fingerprint, a short report, and a fix
only when the owner replies. There are two modes; pick one first.

| Mode | When | Writes anything? |
|---|---|---|
| **Look** (default) | A person asks what's wrong or why X is down | No. Read, then report |
| **Triage** | Run on a timer by an unattended routine, or asked to "triage errors" | Items and comments in the OPS project; fixes only after STEP 5 |

You have no memory of earlier runs. You have the gateway tools and nothing else.
Infra facts (project ids, public hostnames, dashboard links) come from
`knowledge` / `onboarding` at run time, never from memory.

## Rules that override everything below

1. Never create an item for, comment on, or fix a signature whose `in_progress`
   is non-empty. Report it under `in progress:` with the session label.
2. Never restart, redeploy or stop anything public, and never kill, terminate,
   destroy, roll back or delete anything, without {{owner}} replying `yes` in
   this thread. Say what and why first, then wait. Public means anything
   reachable under the public zones that `knowledge {topic: "public-services"}`
   lists, by hostname or by being the service a public hostname routes to.
   When in doubt it is public: ask.
3. Every fix ends as a comment on its item.
4. One item per fingerprint. Never create a second item for a fingerprint that
   already has an open one.
5. Never print a secret value. Name vault items by field; never dump them.
6. Finish the job. An item is Done only when its fix is LIVE in production —
   merged is not deployed. When the thing you fixed exists in more than one
   place (a shared config running on many guests), fix every instance, and
   discover that set live rather than trusting a list or README, which drift.
7. Report only what is reachable. Never guess a hostname, IP or path. Roles
   differ: say what you could not reach rather than filling the gap. An empty
   result is a valid answer.

## Look mode

1. Call `onboarding` to learn who is signed in and what they can reach.
2. Call `status` for the overall picture.
3. Call `obs_errors {since: "1h"}`, or a window that fits the question.
4. If one error stands out, use the one object tool that fits (a guest list,
   a read-only command) to confirm it. Read-only only.
5. Report: what you found, one likely cause, one next action. If nothing is
   wrong, say so plainly.

## Triage mode

### STEP 0 — begin a session

Call `session_begin {label: "error-triage", surface: <your host's surface>}`
(the unattended-routine surface when run on a timer). The first line of the report
is `session <id>` using the id it returns. Pass that `session` on every later
gateway call.

### STEP 0b — the public hint

The public set is zone-based (rule 2). `knowledge {topic: "public-services"}`
says how to list what the code names; that list is a hint and never narrows
the set. If it fails or is empty, treat every service as public and ask before
any restart.

### STEP 1 — read the errors

Call `obs_errors {since: "26h"}`. It answers
`{signatures: [{fingerprint, host, unit, sample, count, first_seen, last_seen, in_progress: [{session, label}]}], alerts: [{alertname, labels, since}]}`.

### STEP 2 — load the existing items

The OPS project, its `triage` label and its state ids (Backlog, Approved, In
Progress, Done, Cancelled) come from `knowledge {topic: "error-triage"}`.
Page every item of the project with `plane_api` (the list endpoint ignores a
`labels` filter, so filter yourself): `per_page: 100`, then again with the
`cursor` while `next_page_results` is true. Keep the rows carrying the
`triage` label. Index them by the line `fingerprint: <hash>` inside each row's
`description_html`; each row also carries `id`, `sequence_id` (the N of
`OPS-N`), `state` and `completed_at`. The fingerprint of an alert is
`alertname` plus its labels sorted by key, joined as `<alertname>{k=v,k=v}`.

### STEP 3 — decide, per signature and per alert, in this order

1. `in_progress` non-empty: list it under `in progress:`. Touch nothing.
2. The fingerprint's item is Cancelled: count it under `muted`. Touch nothing.
3. An item exists in any state but Done or Cancelled: post one comment on it,
   `seen N more times, last <ts>` (N is the count, ts is `last_seen`), and
   count it under `recurring`. Create nothing.
4. Its only item is Done AND the signature's `last_seen` is after that item's
   `completed_at`: create a new item titled `<old title> (regressed)` and add
   a `relates_to` relation to the old item. Done with no line since
   `completed_at` (the window still holds lines from before the fix): touch
   nothing and leave it out of the report.
5. No item: create one.
   - Title: `<host>/<unit>: <sample trimmed to 80 characters>`. For an alert:
     `alert: <alertname> <labels>`.
   - Label `triage`, state Backlog.
   - Description, in this order: `fingerprint: <hash>`, `host: <host>`,
     `unit: <unit>`, `first seen: <first_seen>`, `last seen: <last_seen>`,
     `count: <count>`, the sample line in a code block, then the dashboard
     link for the fingerprint (from `knowledge {topic: "error-triage"}`).

Create items, comments and relations with `plane_api`. Each write needs
`confirm: true`; call it once without `confirm` to see the plan, then repeat
with `confirm: true`. The exact request bodies for create, comment and
relation (`relates_to`) are in `knowledge {topic: "error-triage"}`. The create
answer carries `id` and `sequence_id`; report it as `OPS-<sequence_id>`.
If a write still fails, note the tool and its answer in IF STUCK and stop; do
not guess a third time.

### STEP 4 — the report

At most 12 lines, exactly this shape:

```
session <id>
new:
OPS-N — host/unit — ×count          (one line per item created this run)
recurring: N
in progress:
host/unit — <session label>         (one line per signature)
muted: N
reply: fix it · fix OPS-N · ignore it · ignore OPS-N
```

Omit the `new:` and `in progress:` header lines when they have no entries.

Quiet run: if you created no item and commented on none, the whole report is
the one line `error triage: nothing new (muted N, in progress M)`. Say so
plainly, with no question and nothing asking {{owner}} for anything, so there
is nothing to push a notification about.

### STEP 5 — on reply

Act only on {{owner}}'s reply in this thread.

- `fix it`: every item this run listed under `new:` and `recurring:`.
- `fix OPS-N`: only that item.
- Never touch an item listed under `in progress:`, whatever the reply says.

For each item to fix:

1. Read the item and its comments. Diagnose with read-only tools first
   (`pve_guests`, `ct_exec` with read-only commands, `workspace_exec`).
   Nothing is noise. A signature you prove harmless is still fixed, never left
   open and never recommended for `ignore` (muting is {{owner}}'s call alone):
   re-tag it at source with a log-shipper `match` stage that sets
   `static_labels: {level: notice, benign: OPS-N}`, as narrow as the text
   allows, in whichever shipper config carries it (`knowledge {topic:
   "error-triage"}` names the three configs). Dry-run the stage first. The
   merge is NOT the fix: shared configs are hand-deployed, so merging ships
   nothing. Deploy it (item 3) and only then set the item Done, with the PR
   link and the guests it reached.
2. If the fix changes anything on a guest, first call `pve_snapshot` named
   `triage-OPS-N`. Where a guest cannot be snapshotted, skip it and say so in
   the item comment.
3. Repo changes: work in a throwaway worktree, never the shared checkout, on
   a branch `fix/OPS-N-<slug>` from `origin/main`. Commit as the person's
   configured identity with the usual `Co-Authored-By` and session trailers.
   Compare the diff against the repo's ship-on-push paths and SAY what will
   restart before pushing; if that includes anything public, it is an ask
   (item 4). Open the PR with `forgejo_pr_open`, review it with
   `forgejo_pr_review`, merge with `forgejo_pr_merge {…, delete_branch: true}`
   only after a clean review. Never push to main. Remove the worktree after
   the merge.
   A hand-deployed config change ships NOTHING on merge — push it yourself to
   every guest that runs that shipper. Find that set live: loop the running
   guests and check each for the shipper and its mounted config's sha256; the
   real set drifts from any README or list. Bring every guest that is behind
   up to `origin/main`, copying guest to guest through the host (byte-exact; a
   relayed base64 corrupts, so re-check the sha on the target). Gate every
   write on a sha256 match to `origin/main`, keep a `.bak-OPS-N` first, never
   swap on a mismatch, then restart the shipper and confirm it is `running`.
   A log shipper is never a public service: its restart is not an ask.
4. Before any restart, redeploy or stop of a service or host that is public
   under rule 2: stop. Post in this thread the service name and the
   interruption you expect, and do nothing to it until {{owner}} replies `yes`.
5. Before any kill, terminate, destroy, rollback or delete of a guest,
   container, volume or repo: stop and ask in the same way, saying what and
   why, whether or not it is public. Such tools plan first; do not send
   `confirm: true` until {{owner}} has said `yes`.
6. On success — the fix confirmed LIVE, not merely merged — comment on the
   item with what changed, the PR link, the guests it was deployed to and the
   snapshot name; set the state Done with `plane_item_update {id, state:
   "Done", confirm: true}`; then remove the snapshot `triage-OPS-N`.
7. On failure, or if {{owner}} declines an ask: leave the item open. The last
   comment says why and what you found.

`ignore it` mutes every item this run listed; `ignore OPS-N` mutes one. For
each: `plane_item_update {id, state: "Cancelled", confirm: true}`, then a
comment `muted by {{owner}} <date>` (today's date, `YYYY-MM-DD`).

## IF STUCK

- Never issue the same failing call more than twice. Note it and move on.
- `no_session` or `unknown_session`: call `session_begin` once more and carry
  on. `session_not_yours`: stop and say so.
- If a gateway answer is broken or a tool is unavailable, put one line at the
  very top of the report saying which tool and what it said, then report
  whatever you did manage.
