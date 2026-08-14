# Workflows

Cross-module, end-to-end user journeys. Where a spec answers "what does this module do?",
a workflow answers "what does a person actually do on a Tuesday, and what happens across
the modules while they do it?"

| Workflow | Journey | Modules |
|---|---|---|
| [wf-01](wf-01-dataset-to-model.md) | Raw file → validated Dataset Version → fitted, diagnosed, approved Model | 01, 02, 06, 07 |
| [wf-02](wf-02-model-to-rating-version.md) | Approved Models → peril structure → rating DAG + rate tables → approved Rating Version | 02, 03, 06 |
| [wf-03](wf-03-rate-change-impact.md) | Proposed rate change → optimisation, dislocation, GIPP → decision | 03, 04, 06 |
| [wf-04](wf-04-deploy-and-monitor.md) | Approved Rating Version → deploy → live scoring → monitoring → alert → action | 03, 05, 06, 07 |
| [wf-05](wf-05-custom-objective-lifecycle.md) | Define a custom objective → certify → approve → use → audit → deprecate | 02, 06, 07 |

## Conventions used in every workflow document

- **Actors** are exactly the names in [`00-overview.md`](../specs/00-overview.md) §1.4.
- Every step names *who* acts, *what* they do, *what data* moves, and *what changes*.
- Each step cites the requirement IDs it exercises, so the workflows double as a
  traceability check: a requirement no workflow reaches is either infrastructure or
  a requirement nobody needs.
- Failure paths are specified, not implied. A journey that only documents the happy path
  is not a specification.
- Each document ends with a **traceability table** and a **timing** estimate, so the
  Phase 1 planning has something to size against.
