# Interactive design prototypes

last_verified: 2026-11-04

Owner-approved design-stage approach. This is guidance for design stories and
prototypes, not permission to implement a backend or relax kit rules.

## Review complete flows with real components

Use the actual shared UI kit components and reusable compositions, never drawn or
locally recreated equivalents. Provide enough local interaction to review the full
journey: navigation and drill-down, selection, form editing and validation,
confirmation, cancellation and return paths. Keep disposable presentation state
in memory. Kit-only composition and shared component reuse remain mandatory;
exceptions require the product owner's explicit approval.

## Record future-backend intent once

For an action that needs a future backend, emit a structured JavaScript console
record through one small shared helper used by the prototype's stories/screens.
Use stable domain action names, relevant entity/context identifiers and the intended
payload. For example, this is an illustrative helper API, not a shipped service:

```js
export function logDesignAction(action, context, payload) {
  const record = structuredClone({
    kind: 'design-action-request', action, context, payload,
  });
  console.info(record);
  return record;
}

logDesignAction('task.move',
  { projectId: 'project-example', taskId: 'task-example' },
  { fromColumnId: 'ready', toColumnId: 'doing' });
```

Choose the helper's home in the existing shared story/prototype support area;
reuse it across flows rather than copying log statements or per-screen helpers.
The record captures intended input, not delivery, authorization, persistence or a
backend result. Use synthetic review identifiers/payloads, never credentials or
sensitive live data. Do not build provisional databases, services, inference
integrations or other backend substitutes, including browser storage used as a
pretend database. This restriction does not prevent local UI presentation state.

## Requests and outcome examples are different

An emitted request must not automatically report backend success. Keep the request
record separate from the selected example state. Where the journey needs them,
provide explicit, reproducible design examples for loading, success, failure,
recovery and conflict (including how the person can recover or resolve it).
Label their status in review material as design examples; successful production
copy within an example describes the intended future outcome, not a live change.
No timer, console call or local fixture transition establishes backend completion.
A screenshot proves appearance; native interaction evidence proves only the local
flow and the emitted records it actually exercises.

## Refine candidate contracts alongside design

Treat stable action names, context identifiers and payload shapes as candidate API
contract inputs. Refine them as flows are reviewed and carry them into the build
handoff with the intent, kit composition, state examples and unresolved questions.
They are not approved/published APIs and do not supersede contract-first review.

Interaction tests may spy on the shared helper/console and assert the exact action,
context identifiers and payload produced by a user gesture. These examples can
inform later API contract tests. They do not prove backend behavior, validation,
authorization, delivery, persistence, conflict handling or successful completion;
those require the implemented backend's own contract/integration evidence.
