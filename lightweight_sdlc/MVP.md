# [PROJECT_NAME] MVP

This optional contract defines the minimum release that proves the product's core value. It is the sole source of MVP inclusion; do not duplicate MVP flags in `BACKLOG.md`.

- Status: [Draft / Active / Ready for release review / Released]
- Last updated: [YYYY-MM-DD]

## MVP Outcome

[Describe the smallest meaningful outcome the MVP must create for its target user.]

## Core End-to-End Journey

1. [The essential user journey from entry to successful outcome.]

## Included Capabilities

Use the exact backlog item name until work begins. When the item enters Building, add its feature ID and keep its status synchronized with its permanent feature record.

| Capability / Backlog Item | Feature ID | Status | Why It Is Required |
| --- | --- | --- | --- |
| [Exact backlog item name] | [Pending / FEAT-XXX] | [Backlog / Building / Testing / Done / Canceled] | [Connection to the MVP outcome] |

Changing this list changes MVP scope and requires explicit user approval.

An included capability marked Canceled blocks release readiness until the user explicitly approves replacing or removing it from MVP scope.

## Non-Goals

- [Capability intentionally excluded from the MVP]

## Release Readiness

- Canonical release record: [Not created / `docs/releases/MVP-RELEASE.md`]

After every included capability reaches Done, the harness automatically evaluates eligibility. When all included capabilities are Done with reviewed passing acceptance, it creates or resumes the one canonical harness-owned release record and continues safe local, no-cost readiness work without another prompt.

- [ ] `RR-001` Every included capability is Done after the user reviewed passing acceptance evidence.
- [ ] `RR-002` The declared core end-to-end smoke case passes.
- [ ] `RR-003` Fresh setup instructions work in the claimed environment.
- [ ] `RR-004` Build and local run/package commands work in the claimed environment.
- [ ] `RR-005` Required automated validation passes.
- [ ] `RR-006` No known unresolved release-blocking defects remain.
- [ ] `RR-007` User-facing, operator, and current-status documentation is consistent.
- [ ] `RR-008` Applicable accessibility promises are verified.
- [ ] `RR-009` Applicable privacy promises are verified.
- [ ] `RR-010` Applicable migration promises are verified.
- [ ] `RR-011` Applicable backup promises are verified.
- [ ] `RR-012` Applicable restore promises are verified.
- [ ] `RR-013` Applicable recovery and rollback promises are verified.
- [ ] `RR-014` An independent Reviewer confirms the completed release evidence.

The canonical release record owns exact statuses and evidence. Each check is exactly `pending`, `pass`, `fail`, `blocked`, or `n/a`; every `n/a` requires a reason, and missing evidence never implies pass.

## Release Approval

The canonical release record owns these independent authority fields. No field or transition grants or implies another.

- Feature Done approval(s): [Per-feature references / incomplete]
- Commit authorization: [Not granted / canonical release-record reference]
- Live or cost-bearing UAT authorization: [Not granted / canonical release-record reference]
- Ready-for-release-review determination: [No / Yes — canonical release-record reference]
- Final MVP release approval: [Not granted / explicit user approval and canonical release-record reference]
- Publish/deploy authorization: [Not granted / canonical release-record reference]

Never mark this MVP Released without the user's separate explicit Final MVP release approval. Never publish or deploy without separate Publish/deploy authorization.
