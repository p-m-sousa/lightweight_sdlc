# [PROJECT_NAME] Architecture

This file is the canonical technical map. Keep it proportional to the product, consistent with the codebase, and constrained by `PRODUCT_VISION.md` plus an active `MVP.md` when present.

Remove non-applicable template rows or subsections after bootstrap. Add a separate ADR, technical design, or diagram only when a consequential decision cannot be explained clearly here.

## Summary

- System shape: [Smallest useful architecture and primary runtime boundary.]
- Quality priorities: [Qualities that drive technical choices, in priority order.]
- Technical non-goals: [Complexity or deployment shapes intentionally excluded.]

## Boundaries and Runtime Units

| Actor, External System, or Runtime Unit | Responsibility / Relationship | Trust or Failure Boundary |
| --- | --- | --- |
| [Name] | [What it owns or what crosses the boundary] | [Authentication, availability, ownership, or failure constraint] |

## Module Map

| Module | Responsibility and Owned Data | Allowed Dependencies | Public Contract / Extension Point |
| --- | --- | --- | --- |
| [Module or layer] | [Single responsibility and data ownership] | [Permitted dependency direction] | [Interface other modules rely on] |

## Structural Invariants

- [Source layout, dependency direction, or naming convention.]
- [Project-wide behavior, trust, or data invariant features must preserve.]

## Data and Integrations

### Data Lifecycle

[Applicable storage, schemas, migrations, retention, deletion, backup, restore, and sensitive-data handling. Remove this subsection when the product owns no persistent data.]

### External Integrations

[Applicable contracts, authentication, timeouts, retries, rate limits, failure behavior, and test substitutes. Remove this subsection when there are no external integrations.]

## Cross-Cutting Constraints

- Security and privacy: [Applicable boundaries and constraints.]
- Reliability and recovery: [Failure handling, durability, and recovery expectations.]
- Performance and scale: [Realistic load, latency, memory, caching, or pagination expectations.]
- Accessibility and platform behavior: [Technical constraints affecting supported surfaces.]
- Operations and observability: [Configuration, environments, logging, diagnostics, and deployment expectations.]
- Compliance: [Applicable obligations; remove when none apply.]

## Initial Toolchain

This is a supported starting baseline, not an allowlist. Feature work may add a justified dependency without rerunning architecture bootstrap; update this file only when the choice changes architecture or project-wide conventions.

| Concern | Choice and Version Policy | Rationale / Compatibility Constraint |
| --- | --- | --- |
| Language and runtime | [Choice] | [Supported versions and reason] |
| Framework / platform SDK | [Choice] | [Compatibility range and reason] |
| Dependency manager | [Choice] | [Lockfile and install policy] |
| Build and run | [Choice] | [Local and release workflow] |
| Formatting, linting, and type checking | [Choice or N/A] | [Required checks] |
| Testing | [Choice] | [Test levels and locations] |
| Rendered validation / UAT | [Built-in Browser plus repository-native end-to-end tool, platform equivalent, or N/A] | [Local target, desktop/mobile coverage, evidence, and fallback policy] |
| Persistence / migrations | [Choice or N/A] | [Schema and migration policy] |
| Deployment | [Choice or Deferred] | [Environment strategy] |

## Exact Commands

Record target-selection syntax so feature work can run focused checks without rediscovering the tool. A full-suite command is a capability, not a default; its use follows the triggers in `AGENTS.md` Efficient Execution.

Guarded command: record the raw target syntax below, but execute every test as `python3 -B <project-root>/.codex/scripts/test_guard.py --root <working-directory> -- <raw-command>`. Do not raise its detected limits without explicit user approval.

| Purpose | Command or Target Syntax | Working Directory | Status | Scope / Trigger |
| --- | --- | --- | --- | --- |
| Setup | `[exact command]` | [path] | [Verified / Configured / Planned] | Fresh environment or dependency change |
| Build | `[exact command]` | [path] | [Verified / Configured / Planned] | When compilation or packaging is affected |
| Run locally | `[exact command]` | [path] | [Verified / Configured / Planned] | Launch supported target |
| Format check | `[exact command or N/A]` | [path] | [Verified / Configured / Planned] | Changed applicable files |
| Lint | `[exact command or N/A]` | [path] | [Verified / Configured / Planned] | Changed applicable files or repository-required check |
| Typecheck | `[exact command or N/A]` | [path] | [Verified / Configured / Planned] | Affected typed project or repository-required check |
| Focused unit/integration tests | `[exact target-selection syntax]` | [path] | [Verified / Configured / Planned] | Tests covering changed behavior and adjacent risk |
| Full automated regression | `[exact command or N/A]` | [path] | [Verified / Configured / Planned] | Only an `AGENTS.md` broad-suite trigger or explicit release gate |
| Feature-specific end-to-end / UAT | `[exact target-selection syntax or N/A]` | [path] | [Verified / Configured / Planned] | Recorded feature cases when an executable journey or integration boundary applies |
| Full end-to-end regression | `[exact command or N/A]` | [path] | [Verified / Configured / Planned] | Only an `AGENTS.md` end-to-end trigger or explicit release gate |
| Deterministic release/package | `[exact local no-publish command or N/A]` | [path] | [Verified / Configured / Planned] | Release readiness; produce locally inspectable output only |
| Publish/deploy | `[exact command or N/A]` | [path] | [Verified / Configured / Planned] | Execute only with separate explicit publish/deploy authorization |

## Decisions and Deferred Questions

| Decision or Deferred Question | Rationale / Constraint | Consequence or Revisit Trigger |
| --- | --- | --- |
| [Decision] | [Evidence and tradeoff] | [Constraint and when to reconsider] |

## Related Standards

- `PRODUCT_VISION.md` defines product direction and trust promises.
- Active `MVP.md` defines the minimum release outcome and included capabilities.
- `CLEAN_CODE.md` defines universal and project-specific coding rules.
- `DESIGN_SYSTEM.md` defines user-facing design and accessibility rules.
- `BACKLOG.md` holds future approved product and technical work.
