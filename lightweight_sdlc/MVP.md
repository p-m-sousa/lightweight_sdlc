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

- [ ] Every included capability is Done after the user reviewed passing acceptance evidence.
- [ ] The core end-to-end journey passes independent UAT when it has a meaningful executable user journey.
- [ ] Fresh setup, build, and run instructions work in the supported environment.
- [ ] Required automated validation passes.
- [ ] No known unresolved release-blocking defects remain.
- [ ] User-facing and operator documentation is current.
- [ ] Applicable accessibility and privacy promises are verified.
- [ ] Applicable migration, backup, restore, and recovery promises are verified.

Mark a non-applicable check `N/A` with a short reason rather than silently omitting it.

## Release Approval

Feature Done approval and commit authorization do not constitute MVP release approval.

- Ready for release review: [Yes / No]
- User approved MVP release: [Yes / No]
- Approval date and notes: [YYYY-MM-DD — notes]
