# FEAT-102 Confirmed assistant actions

- Status: Building
- Source backlog item: `Confirmed assistant actions`
- Created: 2026-08-03
- Updated: 2026-08-03
- Delivery profile: deep
- Surface tags: web-ui, web-api, agentic-ai, integration
- Planning route: delegated
- Review route: reviewer-deep
- Acceptance route: independent-uat

## Scope and Plan

- Vision and MVP fit: Lets the assistant propose useful actions without weakening user control.
- In scope: Tool allowlist, preview, explicit confirmation, execution result, and audit evidence.
- Non-goals: Autonomous or background execution.

1. Separate model proposals from validated tool requests and confirmed execution.
2. Add deterministic integration substitutes and adversarial prompt-injection coverage.

## Acceptance Criteria and Cases

- AC-1: No consequential tool runs before explicit confirmation.
- AC-2: Untrusted model output cannot select an unapproved tool or argument.

| ID | Preconditions / Test Data | End-User Steps | Expected Result | Required Evidence |
| --- | --- | --- | --- | --- |
| UAT-1 | Disposable account and fake tool service | Ask for an action, inspect preview, cancel | No tool call occurs | Visible canceled state and zero fake-tool calls |
| UAT-2 | Prompt-injection fixture | Ask assistant to follow injected instructions | Request is rejected safely | User-facing recovery and validation log |

- Core case for rework smoke coverage: `UAT-1`

## Implementation and Validation

- Implementation notes: Pending.
- Focused checks: Pending.
- Broad-suite trigger: Public tool contract; full automated suite required.
- Code self-check: Pending
- Design self-check: Pending

## Review Cycles

### Review Cycle 1

- Review agent: reviewer-deep
- Verdict: Pending
- Findings and dispositions: Pending
- Fix verification: N/A
- Track proposals awaiting approval: None

## Acceptance and Rework Cycles

No cycles yet.
