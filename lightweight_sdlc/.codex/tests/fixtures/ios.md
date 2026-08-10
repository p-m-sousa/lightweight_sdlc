# FEAT-103 Offline recipe editing

- Status: Building
- Source backlog item: `Offline recipe editing`
- Created: 2026-08-03
- Updated: 2026-08-03
- Delivery profile: deep
- Surface tags: ios, data
- Planning route: delegated
- Review route: sol-high
- Acceptance route: independent-uat

## Scope and Plan

- Vision and MVP fit: Keeps user-owned recipes editable without connectivity.
- In scope: SwiftUI editing, validation, persistence, migration, and recovery behavior.
- Non-goals: Cross-device sync.

1. Add a versioned persistence change and migration fixture.
2. Build an accessible editor using existing SwiftUI patterns.

## Acceptance Criteria and Cases

- AC-1: A valid offline edit survives relaunch.
- AC-2: Existing stored recipes migrate without loss.

| ID | Preconditions / Test Data | End-User Steps | Expected Result | Required Evidence |
| --- | --- | --- | --- | --- |
| UAT-1 | Simulator with an existing recipe | Disable network, edit, save, relaunch | Edited recipe is intact | Visible values before and after relaunch |
| UAT-2 | Pre-migration fixture | Launch upgraded app and open recipe | Recipe opens without loss | Visible migrated content and migration log |

- Core case for rework smoke coverage: `UAT-1`

## Implementation and Validation

- Implementation notes: Pending.
- Focused checks: Pending.
- Broad-suite trigger: Schema migration; full automated regression required.
- Code self-check: Pending
- Design self-check: Pending

## Review Cycles

### Review Cycle 1

- Model and effort: Sol High
- Verdict: Pending
- Findings and dispositions: Pending
- Fix verification: N/A
- Track proposals awaiting approval: None

## Acceptance and Rework Cycles

No cycles yet.
