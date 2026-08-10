# AGENTS.md

This is the builder's always-on manual. `KANBAN.md` owns transitions; the feature record owns evidence; named documents own product, architecture, code, and design rules.

## Authority and Scope

- Apply the `PRODUCT_VISION.md` Decision Filter before adding, changing, or prioritizing product scope. `MVP.md`, when active, is the sole source of MVP inclusion.
- `$product-owner` owns bootstrap, refinement, rescope, and discovery; Architect is conditional afterward. Pulls and defects use `KANBAN.md`.
- A request to pull an exact backlog item authorizes the full autonomous lifecycle through passing acceptance, stopping in Testing for human Done approval.
- Ask only for a material product, MVP, design, cost, permission, destructive, safety, or scope decision. Do not track follow-ups without approval.
- Keep Done, commit, cancellation, cost, and MVP release approvals separate.
- Preserve unrelated work. Never broaden work for an adjacent opportunity.

## Delivery Profile

Before creating the feature record, classify the work and record its profile, surface tags, and routes.

Use `deep` when the work affects authentication, authorization, privacy, security, destructive behavior, payments, schemas or migrations, persistence guarantees, public contracts, shared runtime configuration, caching, concurrency, multiple journeys, consequential integrations, external side effects, architecture boundaries, or shared journey infrastructure.

Also use `deep` for agent/model orchestration, tool permissions, prompt injection, untrusted model output, evaluations, AI costs or autonomy, or a new iOS subsystem, integration, background task, persistence mechanism, App Intent, or unfamiliar concurrency boundary. Uncertainty defaults to `deep`.

| Profile | Planning | Review | Acceptance |
| --- | --- | --- | --- |
| `standard` | Primary builder | Independent `reviewer`, Terra High | Builder only when no meaningful black-box journey exists; otherwise independent `uat` |
| `deep` | Independent `planner`, Terra Medium | Independent `reviewer`, Sol High | Independent `uat`, Terra Medium |

Independent UAT is required for user-visible behavior/navigation, responsive/accessibility behavior, persistence, permissions, integrations, AI behavior, and executable iOS behavior. Builder acceptance is limited to docs, internal refactors, tests/tooling, and infrastructure without a meaningful user journey.

If standard review discovers a deep trigger, obtain focused Sol-High reviewer clearance before Testing. Reuse the same reviewer for fixes and the same UAT agent for retests.

## Delegation

- Spawn every role with `fork_turns="none"`. Planner, Reviewer, and UAT receive only root, item/feature, profile, tags, and pass type; Architect receives its role-defined product handoff.
- The Planner is conditional; independent review is mandatory; UAT is adaptive as defined above. Builder self-review never replaces the Reviewer.
- After 15 silent minutes request status, repeat after 10, and interrupt after 5 more only if still silent. Inspect the write scope before one replacement attempt.
- Use Standard speed. Do not enable Fast mode for this harness.

## Context and Validation

At phase entry, use the read-only packet as a starting index, never an evidence cap:

| Phase | Command |
| --- | --- |
| Plan | `python3 -B .codex/scripts/context_router.py plan --item "<exact backlog item>"` |
| Build | `python3 -B .codex/scripts/context_router.py build --feature docs/features/FEAT-XXX.md` |
| Review | `python3 -B .codex/scripts/context_router.py review --feature docs/features/FEAT-XXX.md` |
| UAT | `python3 -B .codex/scripts/context_router.py uat --feature docs/features/FEAT-XXX.md` |

Expand into affected code, tests, callers, configuration, schemas, migrations, or complete document sections whenever correctness requires it. Prefer targeted output, and re-query a narrow range when tool output is truncated.

- Before review, run applicable static checks, affected unit/integration tests, and feature-specific end-to-end coverage when the change crosses an executable journey or integration boundary.
- Run full automated regression only for shared/foundational code, public contracts, schemas/migrations, auth or permissions, dependencies, runtime configuration, concurrency, caches/global state, a focused failure indicating wider risk, or an explicit architecture/release gate.
- Run full end-to-end regression only for shared journey infrastructure, risk across multiple existing journeys, inability to isolate with targeted coverage, or an explicit release gate.
- After fixes, rerun failed/affected checks plus cheap relevant static checks. Reuse current results and record commands once.
- Apply `CLEAN_CODE.md` after the final implementation pass and relevant fixes. Apply `DESIGN_SYSTEM.md` for user-facing work. Match nearby conventions unless a material standards conflict requires user direction.
- Update README when purpose, surfaces, setup/run/validation, status, or contributor guidance changes; link to canonical detail.

## Records and Safety

- Create the next unused `docs/features/FEAT-XXX.md` from the template only after the planning gate passes. Its status and evidence are canonical; keep its linked Kanban card synchronized.
- Store planning, checks, review findings and dispositions, Track proposals, acceptance evidence, rework, efficiency metadata, and final disposition only in the feature record.
- Use local, staging, or disposable UAT data. Consequential external actions require explicit authorization.
- Move Testing to Done only after passing acceptance and explicit user approval. Commit only when that approval authorizes it. Cancel Building or Testing work only with explicit approval and remove only isolatable feature changes.
- Keep this file concise. Put transitions in `KANBAN.md`, role behavior in custom-agent files, code rules in `CLEAN_CODE.md`, and UI rules in `DESIGN_SYSTEM.md`.
