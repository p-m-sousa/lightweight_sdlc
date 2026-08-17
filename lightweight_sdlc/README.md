# Lightweight SDLC Agent Workflow

A repo-based harness for agent-assisted product discovery, architecture, feature delivery, independent review, risk-adaptive user acceptance, and human approval.

The default feature path is:

**Profile → Plan → Build → Independent Review → Acceptance ↔ Fix and Focused Review → Human Done Approval → Automatic Release Readiness → Independent Evidence Review → Human Release Approval**

One backlog selection authorizes the agent-owned loop through passing acceptance. Done, commit authorization, cost commitments, cancellation, backlog additions, and MVP release remain explicit human decisions.

> This distribution README is not project content and is not counted as a token optimization. If it remains in a duplicated harness, Product Owner replaces it with the project README after bootstrap architecture completes.

## Current Status

This distribution contains reusable, uninstantiated process templates. A copied project records real MVP/release status in `MVP.md`, its project README, and the single harness-owned `docs/releases/MVP-RELEASE.md` created automatically when eligible.

The bundled Python scripts and contract tests require Python 3.11 or newer.

## What the Harness Preserves

- Explicit Product Owner bootstrap, proportional in-flight refinement, pivot/rescope, and new-feature discovery with approved Product Vision, design direction, Backlog, and optional MVP.
- Autonomous, cost-gated architecture with exact build, validation, and executable acceptance commands.
- A permanent feature record for planning, implementation, checks, review, acceptance, rework, efficiency, and final disposition.
- A concise project README created at bootstrap and maintained whenever product, platform, setup, validation, status, or contributor guidance changes.
- Mandatory independent code review and mandatory fixes for valid Blocking and Should-fix findings.
- UAT as a lifecycle gate, with independent execution for meaningful user journeys and builder execution only for low-risk work without such a journey.
- Automatic post-Done MVP eligibility, append-only readiness evidence, and independent release-evidence review without a follow-up prompt.
- Human control over Done, commits, cancellation, tracked follow-ups, new costs, and MVP release.

## Usage-Efficient Operating Model

Every feature is classified before Building:

| Profile | Planning | Review | Acceptance |
| --- | --- | --- | --- |
| `standard` | Primary builder | Independent `reviewer-standard` | Builder only without a meaningful black-box journey; otherwise independent `uat` |
| `deep` | Independent `planner` | Independent `reviewer-deep` | Independent `uat` |

Deep triggers include auth/security/privacy, schemas or migrations, persistence guarantees, public contracts, shared configuration/state/concurrency, payments or consequential integrations, architecture boundaries, agent/model/tool orchestration, prompt-injection and untrusted-output boundaries, AI evaluations/cost/autonomy, and new iOS subsystems or platform integrations. Uncertainty defaults to deep.

Independent UAT is required for user-visible behavior, navigation, responsive/accessibility behavior, persistence, permissions, integrations, AI-generated or AI-executed behavior, and executable iOS behavior.

Every delegated role pins its own model and reasoning effort in its own definition file, from the single table in `.codex/authority.toml`. Nothing about authority is passed at spawn time: an attribute a caller must remember to pass is a silent fallback to the runtime default that produces a cheaper result looking identical to a correct one. Where authority varies by profile, there is one agent per authority level rather than one agent plus a remembered override, and a contract test asserts their behavioral instructions stay byte-identical so only authority differs. Process documents name agents only. Standard speed is required because Fast mode consumes usage faster.

All custom agents start with `fork_turns="none"` and a compact repository-backed assignment instead of inherited interview and implementation history. Each role preflights required capabilities, uses an equivalent in-scope workaround when available, and otherwise returns an immediate precise blocker; subagents never install dependencies or issue tool approval requests. The same Reviewer and UAT threads are reused for focused rework.

## Roles

- **Product Owner skill:** explicitly approves bootstrap, in-flight refinement, pivot/rescope, or new-feature product changes and invokes architecture only when required.
- **Architect:** chooses or verifies the smallest product-correct technical foundation at bootstrap and after architecture-relevant approved product changes.
- **Primary builder:** classifies risk, plans standard work, owns state and implementation, runs focused checks, applies fixes, and executes low-risk acceptance.
- **Planner:** read-only and conditional for deep-profile features.
- **Reviewer:** read-only, independent, and mandatory for every feature and completed release-evidence review.
- **UAT:** workspace-write only to the assigned feature's acceptance section and conditional on the recorded acceptance route.

## Runtime Files

| Path | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Always-on authority, risk routing, delegation, and validation rules. |
| [.codex/authority.toml](.codex/authority.toml) | The one declared authority table: model and effort per role, review-route vocabulary, document guard, and session-log location. |
| [.codex/config.toml](.codex/config.toml) | Primary-thread and default subagent authority plus concurrency limits. |
| [.codex/authority_baseline.json](.codex/authority_baseline.json) | Explicit, shrink-only accepted-gap baseline for the compliance audit; ships empty. |
| [.codex/agents/](.codex/agents/) | Architect, conditional Planner, the two mandatory Reviewer authority levels, and adaptive UAT definitions, each pinning its own authority. |
| [.codex/scripts/context_router.py](.codex/scripts/context_router.py) | Read-only, profile-aware, budgeted phase context packets. |
| [.codex/scripts/test_guard.py](.codex/scripts/test_guard.py) | Deterministic host/container resource detection and guarded test execution. |
| [.codex/scripts/authority_audit.py](.codex/scripts/authority_audit.py) | Detective control over recorded session logs: authority compliance and token usage. |
| [.codex/tests/](.codex/tests/) | Static contracts and representative web, agentic-AI, iOS, and release router fixtures. |
| [.agents/skills/product-owner/](.agents/skills/product-owner/) | Product discovery, approvals, backlog, and MVP workflow. |
| [PRODUCT_VISION.md](PRODUCT_VISION.md) | North Star, trust promise, principles, and Decision Filter. |
| [MVP.md](MVP.md) | Optional minimum release outcome and included capabilities. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Boundaries, modules, constraints, toolchain, commands, and decisions. |
| [CLEAN_CODE.md](CLEAN_CODE.md) | Universal and project-specific coding rules. |
| [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) | Universal and project-specific UI/accessibility rules. |
| [BACKLOG.md](BACKLOG.md) | Approved candidate product and technical work. |
| [KANBAN.md](KANBAN.md) | Canonical delivery transition procedure and board. |
| [docs/features/TEMPLATE.md](docs/features/TEMPLATE.md) | Single permanent feature-record contract. |
| [docs/releases/TEMPLATE.md](docs/releases/TEMPLATE.md) | Canonical harness-owned MVP release-readiness record contract. |
| [UI_TWEAKS.md](UI_TWEAKS.md) | User-approved lightweight UI polish. |

The `.codex/tests/` suite verifies configuration, pinned authority, prompt and injected-section ceilings, lifecycle/release contracts, packet behavior, Git-state reporting, the audit's compliance and usage modes, and representative web UI, agentic web app, iOS, and release-readiness routes. Run it from the copied harness root with Python 3.11 or newer:

```bash
python3 -m unittest discover -s .codex/tests -p 'test_*.py'
```

## Delegated Authority

The distribution ships no model identifiers. `.codex/authority.toml` declares three placeholders — `[PRIMARY_MODEL]`, `[SUBAGENT_MODEL]`, and `[ELEVATED_MODEL]` — and maps every role to one of them plus a reasoning effort:

| Agent | Model | Effort |
| --- | --- | --- |
| `planner` | `[SUBAGENT_MODEL]` | medium |
| `reviewer-standard` | `[SUBAGENT_MODEL]` | high |
| `reviewer-deep` | `[ELEVATED_MODEL]` | high |
| `uat` | `[SUBAGENT_MODEL]` | medium |
| `architect` | `[ELEVATED_MODEL]` | high |

An adopting project replaces each placeholder with a real model identifier from its runtime, in `.codex/authority.toml`, `.codex/config.toml`, and each `.codex/agents/*.toml` definition. Two placeholders may resolve to the same identifier. The contract suite fails until every definition matches the table, so a role cannot quietly fall back to the runtime default.

Review-route vocabulary is project vocabulary: `[routes.review]` maps each accepted `Review route:` value in a feature record to the agent that must run it. Rename its keys freely and keep the values pointing at real agents; the audit reads that table instead of hard-coding route names.

### Auditing What Actually Ran

Pinned definitions are the preventive control. The detective control behind them reads the rollout logs the runtime already writes — role, model, effort, and token usage per session — and instruments nothing new:

```bash
python3 -B .codex/scripts/authority_audit.py --mode compliance
```

Compliance checks two things. Every configured review session must have run at its role's declared authority, which needs no feature correlation and is exact. For a session attributed to a `FEAT-XXX` record whose current review route exists in `[routes.review]`, the recorded agent must also match that route. Attribution is exact or absent: a delegate names its assigned feature record when it generates the phase packet, and a session without that command is reported as unattributed rather than guessed at from record mentions.

Use `--mode usage` for input, cached-input, and output tokens rolled up by role and by attributable feature; all other sessions are grouped as unattributed.

A fresh copy has no session history, so the audit reports `no history` and exits 0 — absence of evidence never fails a new project. Accepted gaps go in `.codex/authority_baseline.json`, which is shrink-only: its `max_entries` cap must always equal the number of entries, so accepting a gap is an explicit, reviewable edit and accidental growth fails the contract suite. The shipped baseline is empty and must never be seeded with a project's history.

## Copy Into a Project

You may duplicate and rename the full harness folder, including hidden `.codex`, `.agents`, and test files. Product Owner replaces this distribution README after bootstrap architecture completes. When copying into an existing repository instead, do not overwrite its real project README or `.gitignore`.

Then:

0. Confirm Python 3.11 or newer is available, replace the model placeholders described under Delegated Authority, and run the contract-test command above to confirm the table and definitions agree.
1. Start a Codex task in Plan mode and explicitly invoke `$product-owner`.
2. Approve Product Vision, product-specific design direction, Backlog, optional storyboard, and MVP decision.
3. When requested, switch out of Plan mode and reply `Write the approved product changes and complete the product handoff.`
4. Product Owner writes only approved product artifacts and spawns `architect` without inherited conversation history.
5. Resolve only a required new cost commitment if Architect identifies one.
6. Product Owner creates the project README from the approved product foundation and finalized architecture.
7. Confirm all retained templates were adapted and architecture records exact focused and broad validation plus browser/Simulator/API acceptance paths.

For an in-progress product, use `$product-owner` to reconcile observed feedback with product intent, pivot/rescope, or discover new features. It classifies defects and lightweight tweaks before reopening product decisions, assesses Backlog/Building/Testing/Done/MVP impact without rewriting feature history, and invokes Architect only for an architecture-relevant approved delta. Pulling an already-approved backlog item uses the feature lifecycle directly.

When upgrading an existing harness, migrate only active feature records: add the five routing fields, preserve all history, and move any existing review findings and dispositions into the matching feature record before removing old review artifacts. Do not rewrite completed feature history.

## Feature Lifecycle

### Backlog and Profiling

Backlog candidates normally have no feature ID. Product Owner makes each new or revised candidate the thinnest coherent vertical slice that produces an independently acceptable outcome, including additions made during refinement. A pull begins by applying the Product Vision Decision Filter and assigning delivery profile, surface tags, and Planning/Review/Acceptance routes.

The primary builder plans standard work. Deep work receives an independent Planner. Only an aligned, executable plan enters Building.

### Building and Review

The builder creates the next `FEAT-XXX` record, updates the linked board card and active MVP when applicable, implements the smallest approved behavior, updates stale README sections, and records focused checks once. Each record states the README impact or why no update was needed.

Every feature receives independent review. Standard work routes to `reviewer-standard`; deep work routes to `reviewer-deep`. A deep trigger found during standard review promotes the record, changes its review route, and requires focused `reviewer-deep` clearance. Blocking and Should-fix findings are resolved through the same Reviewer thread before Testing. A Reviewer tooling or access blocker leaves the feature in Building and is surfaced immediately. Track proposals remain non-blocking and require approval before backlog addition.

### Testing and Acceptance

After review clearance, the record moves to Testing. Independent-UAT routes spawn the `uat` agent. Builder routes execute the same recorded black-box cases in the existing builder context.

Initial acceptance runs all feature cases. Rework reruns failed/affected cases plus the core case; it expands to every feature case only when shared behavior changed. Full repository end-to-end regression requires a documented broad trigger.

A failure returns the same feature to Building for the smallest fix, affected validation, and focused review. The same UAT thread retests after clearance. A blocker remains in Testing until its environment, permission, credential, tooling, safety, or expectation issue is resolved.

A passing verdict remains in Testing for human review. Only explicit approval moves it to Done and may authorize a commit.

### Done, Canceled, and MVP Release

Done and cancellation require explicit approval. Cancellation removes only isolatable feature work. After every active-MVP Done, the builder immediately evaluates eligibility. Once all included capabilities are Done with reviewed passing acceptance, it creates or resumes exactly `docs/releases/MVP-RELEASE.md` and continues safe local/no-cost evidence mapping, documentation checks, deterministic tooling, and guarded validation without another prompt.

The record freezes the MVP/checklist snapshot and platform/runtime claims, uses stable checks with `pending|pass|fail|blocked|n/a`, and appends readiness/rework cycles. Missing evidence never passes; `n/a` needs a reason. Remediation reruns affected checks plus core smoke, expanding only for existing broad-suite triggers. A missing product deliverable becomes a prepared decision with evidence, proposed scope, and a recommended backlog item; product work starts only after normal scope authorization, links its feature record, and automatically resumes readiness after Done.

Independent review of completed release evidence is required before the readiness determination. Feature Done, commit, live/cost UAT, readiness, final MVP release, and publish/deploy authorities remain separate. Only the user's separate explicit release approval marks the MVP Released; publish/deploy needs its own authorization.

## Context Routing

Each phase generates a current packet. Packets use one source range per block, include only profile-relevant design/AI context, distinguish unavailable/clean/changed Git states, and index the canonical release record, active MVP readiness/approval, platform/runtime claims, release commands, and current-status documentation for a release pass.

The default 4,000-character budget meters supplementary blocks only. Required blocks are the phase's subject matter — the feature or release record under work — and always emit, so a large mandatory record can never crowd out the standards a phase needs. Supplementary blocks are admitted cheapest first, and an excerpt larger than half of its complete source is dropped in favor of a pointer to that source.

Routed table rows match the row label, not the row body, so a term like `Build` cannot pull in every row that merely mentions building.

Every packet ends with an accounting footer stating what it spent, what was required, and a warning naming each omitted block with its size and the reason it was dropped. Silent omission is the failure mode this design exists to remove.

The packet is never an evidence cap. Agents inspect affected code, callers, tests, configuration, schemas, migrations, or complete sections when correctness requires it.

The router stays in the harness only while representative web UI, agentic-AI, and iOS packets remain at least 30% smaller than the direct canonical context for at least two profiles without losing required decisions, commands, acceptance criteria, or safety constraints.

## Validation Scope

Focused validation is the default: applicable static checks, affected unit/integration tests, and feature-specific end-to-end coverage for an executable journey or integration boundary. Full automated and full end-to-end suites run only for the shared-risk and release triggers in `AGENTS.md`.

Every executable test is launched through `.codex/scripts/test_guard.py`. It derives CPU, current memory headroom, disk reserve, and container limits directly from the environment and applies deterministic worker, Node-heap, aggregate-RSS, disk, and timeout limits sized to preserve normal parallelism. It does not consume Codex user settings. Missing inspection is reported to the user and uses bounded fallback limits without blocking the test; confirmed unsafe headroom still stops it. A higher limit or unguarded exception requires explicit user approval, and missing system permission is requested through Codex's normal approval boundary.

Still-current passing results are reused. After fixes, failed and affected checks rerun; unchanged suites do not repeat merely for a state transition.

## Efficiency Pilot

For the first eight real features, each record captures profile/tags, roles and model effort, review and acceptance cycles, first-handoff Done approval, and credits/tokens when exposed by the Codex surface.

The target is at least 30% lower median usage for comparable standard features without more user-rejected Done handoffs, escaped defects, or routing-caused rework. A quality failure promotes that defect class to deep routing rather than reverting every efficiency gain.

## Canonical Ownership

- `AGENTS.md`: authority, risk routing, delegation, validation, and safety.
- `KANBAN.md`: lifecycle transitions and board.
- `docs/features/FEAT-XXX.md`: all delivery evidence and final disposition.
- `docs/releases/MVP-RELEASE.md`: the single harness-owned, append-only active-MVP release-readiness record.
- Custom agents: role-specific behavior and compact outputs.
- Product, MVP, architecture, code, and design documents: their named subject matter.
- This README: distribution orientation only.
