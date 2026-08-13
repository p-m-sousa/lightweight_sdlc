# MVP Release Readiness Record

This is a harness-owned release record, not a product feature. Instantiate it only at `docs/releases/MVP-RELEASE.md`; create it once for the active MVP, then resume that file. It never receives a feature ID, backlog row, Kanban card, delivery profile, or feature acceptance record.

- Record kind: `harness-owned release readiness`
- Canonical path: `docs/releases/MVP-RELEASE.md`
- Record status: [active / ready for release review / released]
- Created: [YYYY-MM-DD]
- Updated: [YYYY-MM-DD]
- Active MVP source: `MVP.md`
- Frozen snapshot date: [YYYY-MM-DD]
- Frozen source revision: [commit/tree reference or `working tree — <exact evidence reference>`]
- Declared core smoke check: `RR-002`

## Frozen MVP and Checklist Snapshot

Copy the active MVP capability rows and checklist definitions when release readiness begins. This snapshot is immutable. If the user later authorizes an MVP scope change, preserve this snapshot and append the change, authorization, and resulting feature link in a Rework Cycle.

| Included Capability | Feature Record | Done Approval Reference | Reviewed Passing Acceptance Reference |
| --- | --- | --- | --- |
| [Exact capability name] | [docs/features/FEAT-XXX.md] | [Exact section/evidence reference] | [Exact cycle/review reference] |

Stable readiness checks:

| Check ID | Frozen Requirement | Applicability Rule |
| --- | --- | --- |
| RR-001 | Every included capability is Done with reviewed passing acceptance. | Always |
| RR-002 | The declared core end-to-end smoke case passes. | Always; use the documented non-executable consistency case only when no executable journey exists |
| RR-003 | Fresh setup succeeds from the documented instructions. | Always |
| RR-004 | Build and local run/package commands succeed. | Always |
| RR-005 | Required automated validation passes. | Always |
| RR-006 | No known unresolved release-blocking defect remains. | Always |
| RR-007 | User-facing, operator, and current-status documentation is consistent. | Always |
| RR-008 | Accessibility promises are verified. | When the product has a user-facing surface or an explicit accessibility claim |
| RR-009 | Privacy promises and data handling are verified. | When the product handles user or sensitive data or makes a privacy claim |
| RR-010 | Migration promises are verified. | When release changes or depends on persisted schemas/data |
| RR-011 | Backup promises are verified. | When the product owns durable data with a backup claim |
| RR-012 | Restore promises are verified. | When the product owns durable data with a restore claim |
| RR-013 | Recovery and rollback promises are verified. | When Architecture or operations documentation claims them |
| RR-014 | An independent Reviewer confirms the completed release evidence is sufficient and internally consistent. | Always; run only after RR-001 through RR-013 contain no `pending`, `fail`, or `blocked` |

## Supported Platform and Runtime Claims

Claims are the exact release envelope being evaluated, not aspirational coverage.

| Claim ID | OS / Version | Architecture / Device | Runtime / SDK / Browser | Claim Source | Verification Check IDs | Limitations |
| --- | --- | --- | --- | --- | --- | --- |
| PLAT-001 | [Exact OS and version] | [Exact architecture/device] | [Exact version] | [Architecture/README reference] | [RR-IDs] | [None or exact limitation] |

## Deterministic Release Commands and Cases

Copy exact commands and black-box cases from canonical project documentation. Tests must run through `.codex/scripts/test_guard.py`; do not execute live, network, external-side-effect, or cost-bearing cases without their separate authorization.

| Purpose | Reproducible Command or Black-Box Case | Working Directory / Target | Guard / Safety Boundary | Source Reference |
| --- | --- | --- | --- | --- |
| Core smoke | [Exact command or case] | [Exact path/target] | [Guard and disposable-data rule] | [Canonical reference] |
| Setup/build/validation | [Exact command] | [Exact path] | [Guard or deterministic local boundary] | [Architecture/README reference] |

## Readiness and Rework Cycles

Append cycles; never overwrite or delete a completed, failed, or blocked cycle. A correction or superseding result belongs in a later cycle with the earlier evidence referenced.

### Readiness Cycle 1

- Opened: [YYYY-MM-DD]
- Closed: [YYYY-MM-DD / Open]
- Trigger: [Initial automatic eligibility / Post-remediation resume]
- Scope: [All checks / affected check IDs plus RR-002 core smoke / broader scope and recorded trigger]
- Evidence mapping and documentation consistency work: [Exact local work completed]
- Deterministic tooling prepared or run: [Exact local tooling and result]
- Broad-suite trigger: [None / exact existing AGENTS.md trigger and resulting scope]

Every check row must use exactly `pending`, `pass`, `fail`, `blocked`, or `n/a`. Every row requires a reproducible command or black-box case, date, exact environment, evidence reference, and owner/next action. `n/a` also requires a concrete reason. Missing evidence is never a pass.

| Check ID | Status | Reproducible Command or Black-Box Case | Date | Exact Environment | Evidence Reference | Owner / Next Action | N/A Reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RR-001 | pending | [Exact evidence-mapping procedure] | [YYYY-MM-DD] | [Repository revision and local OS/runtime] | [Reference or `missing — not a pass`] | [Owner and next action] | — |
| RR-002 | pending | [Exact core smoke command/case] | [YYYY-MM-DD] | [Exact target, OS, runtime, and test data] | [Reference or `missing — not a pass`] | [Owner and next action] | — |
| RR-003 | pending | [Exact fresh-setup command/case] | [YYYY-MM-DD] | [Exact environment] | [Reference or `missing — not a pass`] | [Owner and next action] | — |
| RR-004 | pending | [Exact build/run command/case] | [YYYY-MM-DD] | [Exact environment] | [Reference or `missing — not a pass`] | [Owner and next action] | — |
| RR-005 | pending | [Exact guarded validation command] | [YYYY-MM-DD] | [Exact environment] | [Reference or `missing — not a pass`] | [Owner and next action] | — |
| RR-006 | pending | [Exact release-blocker query/case] | [YYYY-MM-DD] | [Exact environment] | [Reference or `missing — not a pass`] | [Owner and next action] | — |
| RR-007 | pending | [Exact documentation consistency case] | [YYYY-MM-DD] | [Exact environment] | [Reference or `missing — not a pass`] | [Owner and next action] | — |
| RR-008 | pending | [Exact accessibility command/case] | [YYYY-MM-DD] | [Exact environment] | [Reference or `missing — not a pass`] | [Owner and next action] | — |
| RR-009 | pending | [Exact privacy command/case] | [YYYY-MM-DD] | [Exact environment] | [Reference or `missing — not a pass`] | [Owner and next action] | — |
| RR-010 | pending | [Exact migration command/case] | [YYYY-MM-DD] | [Exact environment] | [Reference or `missing — not a pass`] | [Owner and next action] | — |
| RR-011 | pending | [Exact backup command/case] | [YYYY-MM-DD] | [Exact environment] | [Reference or `missing — not a pass`] | [Owner and next action] | — |
| RR-012 | pending | [Exact restore command/case] | [YYYY-MM-DD] | [Exact environment] | [Reference or `missing — not a pass`] | [Owner and next action] | — |
| RR-013 | pending | [Exact recovery/rollback command/case] | [YYYY-MM-DD] | [Exact environment] | [Reference or `missing — not a pass`] | [Owner and next action] | — |
| RR-014 | pending | [Independent release-evidence review case] | [YYYY-MM-DD] | [Exact repository revision and review environment] | [Reference or `missing — not a pass`] | [Owner and next action] | — |

#### Prepared Product Decisions

When a missing product deliverable causes a check to fail, prepare the decision here and present it to the user. Do not create the backlog item, feature record, MVP capability, or implementation until normal product/MVP/scope authorization is explicit.

| Failed Check ID | Evidence | Proposed Remediation Scope | Recommended Backlog Item | Required Decision | Authorization | Linked Feature Record / Resume Trigger |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [RR-ID] | [Exact evidence] | [Smallest coherent product remediation] | [Prepared title and acceptance outcome] | [Product/MVP/design/scope decision] | [Pending / exact approval reference] | [None until authorized / FEAT-XXX; resume after Done] |

### Rework Cycle 1

- Opened: [YYYY-MM-DD]
- Triggering check IDs and preserved evidence: [RR-IDs and prior-cycle references]
- Authorized remediation scope: [Exact approval reference / local evidence-only correction]
- Product remediation feature: [None / docs/features/FEAT-XXX.md]
- Affected checks to rerun: [RR-IDs]
- Required core smoke: `RR-002`
- Broad-suite trigger: [None / exact existing trigger]
- Outcome and next readiness cycle: [Pending / reference]

Remove this unused placeholder when no rework occurs. Otherwise retain it permanently and append numbered Readiness/Rework cycles.

## Independent Evidence Review

After RR-001 through RR-013 have no `pending`, `fail`, or `blocked`, give an independent Reviewer the release context packet with `pass_type=release-evidence`. Record its evidence-backed verdict in a new Readiness Cycle as RR-014. Only a `pass` permits the ready-for-release-review determination.

- Reviewer and effort: [Independent Reviewer, model/effort]
- Date and exact environment/revision reviewed: [YYYY-MM-DD — details]
- Verdict: [evidence complete / fix evidence before determination / blocked]
- Evidence reference and findings: [Exact references / None]

## Separate Approval Authorities

These fields are independent. No value, transition, or approval in one field grants or implies any other.

- Feature Done approval(s): [Per-feature explicit approval references / incomplete]
- Commit authorization: [Not granted / exact authorized scope, date, and actor]
- Live or cost-bearing UAT authorization: [Not granted / exact authorized action, cost boundary, date, and actor]
- Ready-for-release-review determination: [No / Yes — date, actor, RR-014 pass reference]
- Final MVP release approval: [Not granted / explicit user approval, date, and notes]
- Publish/deploy authorization: [Not granted / exact target, scope, date, and actor]

Do not set `Record status: released` or mark `MVP.md` Released without the user's separate explicit Final MVP release approval. Do not publish or deploy without separate Publish/deploy authorization.
