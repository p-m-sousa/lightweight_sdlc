# AGENTS.md

Builder manual. `KANBAN.md` owns transitions; feature/release records own evidence; named documents own their subjects.

## Authority and Scope

- Apply the `PRODUCT_VISION.md` Decision Filter to product scope. Active `MVP.md` solely owns MVP inclusion.
- `$product-owner` owns bootstrap, refinement, rescope, and discovery; Architect is conditional afterward. Pulls and defects use `KANBAN.md`.
- Pulling an exact backlog item authorizes autonomous work through passing acceptance, stopping in Testing for human Done approval.
- Ask only for a material product/MVP/design/scope decision, cost, permission, credential, safety, destructive action, or unavailable environment. Do not track follow-ups without approval.
- After every active-MVP Done, automatically apply `KANBAN.md` release eligibility and continue safe local no-cost readiness work. Use only `docs/releases/MVP-RELEASE.md`; it is harness-owned, not a feature.
- Keep feature Done, commit, live/cost UAT, release-review readiness, final MVP release, and publish/deploy authorities separate; none implies another.
- Preserve unrelated work. Never broaden work for an adjacent opportunity.

## Delivery Profile

Use `deep` for auth/privacy/security, destructive behavior, payments, schemas/migrations, persistence guarantees, public contracts, shared runtime/state/caching/concurrency/journeys, consequential integrations/effects, architecture boundaries, agent/model/tool orchestration, prompt injection/untrusted output, AI evaluation/cost/autonomy, or a new iOS subsystem/integration/background task/persistence/App Intent. Uncertainty defaults to `deep`.

| Profile | Planning | Review | Acceptance |
| --- | --- | --- | --- |
| `standard` | Primary builder | Independent `reviewer`, Terra High | Builder only when no meaningful black-box journey exists; otherwise independent `uat` |
| `deep` | Independent `planner`, Terra Medium | Independent `reviewer`, Sol High | Independent `uat`, Terra Medium |

Independent UAT covers user-visible/navigation/responsive/accessibility, persistence, permissions, integrations, AI, and executable iOS behavior. Builder acceptance is limited to work without a meaningful user journey.

If standard review discovers a deep trigger, obtain focused Sol-High reviewer clearance before Testing. Reuse the same reviewer for fixes and the same UAT agent for retests.

## Delegation

- Spawn roles with `fork_turns="none"`. Planner/Reviewer/UAT receive only root, item/feature or release path, profile, tags, and pass type; Architect receives its role-defined product handoff.
- Builder self-review never replaces the Reviewer.
- Delegates never install or request tool approval. Preflight tools, dependencies, and access; use an equivalent in-scope fallback or immediately return the exact `blocked` condition.
- After 15 silent minutes request status, repeat after 10, then interrupt after 5; inspect write scope before one replacement.
- Use Standard speed, never Fast mode.

## Context and Validation

At phase entry, use the read-only packet as a starting index:

| Phase | Command |
| --- | --- |
| Plan | `python3 -B .codex/scripts/context_router.py plan --item "<exact backlog item>"` |
| Build | `python3 -B .codex/scripts/context_router.py build --feature docs/features/FEAT-XXX.md` |
| Review | `python3 -B .codex/scripts/context_router.py review --feature docs/features/FEAT-XXX.md` |
| UAT | `python3 -B .codex/scripts/context_router.py uat --feature docs/features/FEAT-XXX.md` |
| Release | `python3 -B .codex/scripts/context_router.py release --release docs/releases/MVP-RELEASE.md` |

Expand whenever correctness requires it; re-query narrow ranges when output truncates.

- Before review, run applicable static checks, affected unit/integration tests, and feature end-to-end coverage for an executable journey or integration boundary.
- Full automated regression requires shared contracts/data/auth/dependencies/runtime/state, wider risk, or an architecture/release gate. Full end-to-end requires shared/multiple journeys, inability to isolate, or a release gate.
- Run every test as `python3 -B .codex/scripts/test_guard.py --root <working-directory> -- <command>`. It derives host/container caps for workers, Node heap, RSS, disk, and time. Raising/bypassing a limit requires approval. Request Codex approval for inspection; if unavailable, alert the user and use the bounded fallback rather than block testing.
- After fixes, rerun failed/affected checks plus cheap static checks. Reuse current results and record commands once.
- Apply `CLEAN_CODE.md` after final implementation/fixes and `DESIGN_SYSTEM.md` for user-facing work. Match nearby conventions absent a material conflict.
- Update README when purpose, surfaces, setup/run/validation, status, or contributor guidance changes; link to canonical detail.

## Records and Safety

- Create the next unused `docs/features/FEAT-XXX.md` from the template only after the planning gate passes. Its status and evidence are canonical; keep its linked Kanban card synchronized.
- Store planning, checks, review, acceptance, rework, efficiency, and disposition only in the feature record.
- Keep release evidence and append-only readiness/rework cycles only in the canonical release record. Missing evidence never passes; every `n/a` needs a reason. Independent release-evidence review precedes readiness, and only explicit user approval marks the MVP Released.
- Use local, staging, or disposable UAT data. Consequential external actions require explicit authorization.
- Move Testing to Done only after passing acceptance and explicit user approval. Commit only when that approval authorizes it. Cancel Building or Testing work only with explicit approval and remove only isolatable feature changes.
- Keep this file concise. Put transitions in `KANBAN.md`, role behavior in custom-agent files, code rules in `CLEAN_CODE.md`, and UI rules in `DESIGN_SYSTEM.md`.
