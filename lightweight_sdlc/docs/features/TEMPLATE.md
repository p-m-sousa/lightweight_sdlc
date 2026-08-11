# [FEATURE-ID] [Feature Name]

- Status: [Building / Testing / Done / Canceled]
- Source backlog item: `[Exact backlog item name]`
- Created: [YYYY-MM-DD]
- Updated: [YYYY-MM-DD]
- Delivery profile: [standard / deep]
- Surface tags: [web-ui / web-api / ios / agentic-ai / data / integration / internal]
- Planning route: [builder / delegated]
- Review route: [terra-high / sol-high]
- Acceptance route: [builder / independent-uat]

## Transition History

| Date | From | To | Reason |
| --- | --- | --- | --- |
| [YYYY-MM-DD] | Backlog | Building | [Planning gate passed.] |

## Scope and Plan

- Vision and MVP fit: [Decision Filter result, constraints, and MVP relationship.]
- In scope: [Observable outcome.]
- Non-goals: [Explicit exclusion.]

1. [Concrete implementation outcome in dependency order.]

## Acceptance Criteria and Cases

- AC-1: [Observable expected result.]

| ID | Preconditions / Test Data | End-User Steps | Expected Result | Required Evidence |
| --- | --- | --- | --- | --- |
| UAT-1 | [Starting state and safety constraints.] | [Actions through the supported surface.] | [Observable result mapped to AC-1.] | [Visible state, navigation, persisted outcome, log, or screenshot.] |

- Core case for rework smoke coverage: `UAT-1`

## Implementation and Validation

- Implementation notes: [Important completed decisions.]
- Focused checks: [Guarded commands, detected limits, scope, and results.]
- Broad-suite trigger: [Trigger and result / None — focused validation used.]
- Code self-check: [Pass / N/A]
- Design self-check: [Pass / N/A]
- README impact: [Updated sections / N/A — documented facts unchanged.]

## Review Cycles

### Review Cycle 1

- Model and effort: [Terra High / Sol High]
- Verdict: [ready for Testing / ready with proposed follow-ups / fix before Testing / blocked]
- Findings and dispositions: [Evidence-backed Blocking, Should fix, Track, and useful FYI items / None.]
- Fix verification: [Focused result / N/A]
- Track proposals awaiting approval: [Summary / None]

Append later review cycles only when rework or risk escalation requires them.

## Acceptance and Rework Cycles

### Acceptance Cycle 1

- Executor: [Primary builder / Independent UAT agent]
- Date: [YYYY-MM-DD]
- Verdict: [pass / fail / blocked]
- Environment: [Target, disposable test data, resource-guard policy/result, tool path, and platform/viewport coverage.]
- Scope: [All feature cases / Failed and affected cases plus core case / All cases because shared behavior changed.]
- Repository-wide end-to-end regression: [Not run / Trigger, command, and result.]

| Case | Result | Observed Behavior | Evidence |
| --- | --- | --- | --- |
| [UAT-ID] | [Pass / Fail / Blocked / Not run] | [Actual versus expected.] | [Concise durable evidence.] |

- Non-blocking observations: [Summary / None]
- Cases requiring retest: [IDs and reason / None]
- Repository write check: [Expected writes only / Blocked with details]

For a failed cycle requiring changes, append a Rework Cycle while Building, then append the next Acceptance Cycle after focused reviewer clearance.

### Rework Cycle 1

- Defect and affected criteria: [Observed failure and AC IDs.]
- Fix and checks: [Smallest fix plus affected validation.]
- Focused reviewer verdict: [ready for Testing / ready with proposed follow-ups / blocked]
- Retest scope: [Affected IDs plus core case / All cases because shared behavior changed]

Remove this unused placeholder when the first acceptance pass succeeds.

## Efficiency and Final Disposition

- Roles and model/effort used: [Builder; optional Planner; Reviewer; optional UAT.]
- Review cycles: [N]
- Acceptance cycles: [N]
- Usage: [Credits/tokens when exposed / Unavailable]
- User approved Done on first handoff: [Yes / No / Pending]
- Final disposition: Pending

When selected, replace `Pending` with exactly one outcome:

- Done: [YYYY-MM-DD — passing acceptance reviewed; approval and commit authorization; MVP update.]
- Canceled: [YYYY-MM-DD — approval, reason, scoped-work disposition, unrelated-work check, backlog and MVP disposition.]
