---
name: cypher-deploy
description: Walks a Builder or Owner through deploying their app to their own guest, on a name they own, behind CypherAuth. Use when someone wants to deploy, ship, or publish an app they built, or asks to tear one down.
---

# cypher-deploy

PURPOSE: get a person's own app running on their own guest, published on
a name they own, behind CypherAuth — plan first, confirm, then act. This
skill never assumes a host, pool, or route; every one of those comes
from a live gateway call for this specific person.

## Who this is for

Builder or Owner only. Call `onboarding` first if role isn't already
confirmed this session. If the role isn't Builder or Owner, say plainly
that deploying isn't available to them and point at `cypher-start` for
what they can do instead — do not attempt any `pve_*` call.

## Steps

1. Confirm role via `onboarding` (Builder or Owner).
2. Ask the gateway what's available before planning anything concrete:
   call `knowledge` for deploy conventions relevant to this person (own
   pool, quota, naming) if the topic exists; fall back to `onboarding`
   for the same facts if it doesn't. Never assume a pool name, quota
   number, or naming convention — read it from whichever call answers.
3. **Build a plan, don't act yet.** The plan states, in plain language:
   - which guest will be created (or reused) and in which pool — this
     person's own pool only, within their quota
   - what the app will be deployed as, and the name it will be
     published on (a name this person owns)
   - that the published route sits behind CypherAuth, so only a
     signed-in, authorized person reaches it
   - the teardown path (see below), so the person knows how to undo
     this before they say yes
4. **Show the plan and ask for confirmation.** Do not call any `pve_*`
   tool, or anything else that creates or changes a guest, before the
   person explicitly confirms the plan as shown.
5. Once confirmed, carry out the plan using only the `pve_*` tools this
   person's role grants, calling each without `confirm` first to see
   the no-op plan the gateway itself returns, then with `confirm` to
   apply it. If any step is refused, stop and report the refusal
   verbatim — don't retry with a broader scope or a different pool to
   work around it.
6. Report back the published name/route and confirm it sits behind
   CypherAuth. This skill does not verify the live route itself beyond
   what the gateway's own response confirms.

## Teardown

To undo a deployment made with this skill: ask to tear it down, and this
skill will plan (then, on confirmation, run) the reverse — removing the
publish/name binding and stopping or destroying the guest it ran on,
using the same plan-first, confirm-then-act flow above. Nothing is
removed without an explicit confirmation of that specific plan.

## Rules

- Plan-first, always. Showing the plan and getting a yes is not
  optional, even for a teardown.
- Builder- and Owner-scoped actions stay inside this person's own pool
  and their own names — never core infra, never another person's guest
  or route. A refusal from the gateway on this point is the system
  working, not an error to route around.
- Never hardcode a pool name, guest ID, hostname, or route — every one
  comes from this person's own `onboarding`/`knowledge` results or from
  the gateway's own plan/confirm responses in this session.
