# CLEAN_CODE.md

This file is the source of truth for code quality. Universal rules stay concise and language-agnostic; project-specific extensions belong at the bottom.

The priority order is: correctness and user trust, clarity, maintainability, security, then measured efficiency. Approved task requirements may add stricter constraints.

## 1. Scope and Simplicity

- Implement the smallest coherent change that satisfies the approved acceptance criteria.
- Do not add speculative features, abstractions, dependencies, or refactors.
- Refactor only when it makes the approved change safer or clearer; preserve behavior with tests.
- Keep unrelated cleanup out of the change and surface it separately for user approval when tracking is warranted.
- Reuse established project patterns unless they conflict with an explicit requirement or standard.

## 2. Clarity and Structure

- Use names that express domain intent and follow the language and repository conventions.
- Keep responsibilities focused and dependencies directional. Split code when separate reasons to change have become entangled.
- Avoid duplicated business knowledge; extract shared behavior when the abstraction is stable and improves understanding.
- Prefer straightforward control flow and explicit side effects.
- Use comments for rationale, constraints, and non-obvious tradeoffs—not to narrate code.
- Remove dead code, exploratory leftovers, and generated artifacts that do not belong in source control.

## 3. Boundaries, Data, and Failures

- Validate untrusted data where it crosses a boundary.
- Preserve documented data ownership, schemas, compatibility, migration, backup, and restore promises.
- Handle expected failures explicitly and provide useful context without exposing secrets or sensitive data.
- Do not swallow errors or use exceptions as routine control flow.
- Keep I/O, persistence, network, and framework concerns behind the project's established boundaries.
- Make destructive or irreversible behavior explicit, confirm it where required, and design recovery when the product promises it.

## 4. Security and Privacy

- Never hardcode, commit, expose, or log credentials, tokens, secrets, or unnecessary personal data.
- Use least privilege and vetted platform or library mechanisms for authentication, authorization, encryption, and sensitive storage.
- Defend realistic inputs against injection, path traversal, unsafe deserialization, and other boundary-specific risks.
- Verify new dependencies exist, are maintained, and are appropriate for the approved scope.

## 5. Tests and Validation

- Add or update tests for meaningful changed behavior, boundaries, regressions, and failure paths.
- Keep tests deterministic and proportionate to risk; use integration or UI tests when unit tests cannot prove the contract.
- Run the exact commands recorded in `ARCHITECTURE.md` plus any checks required by the changed subsystem.
- Do not claim a check passed when it was not run. Record unavailable checks and the reason.
- Re-read the final diff for scope, correctness, documentation, tests, and accidental changes.

## 6. Documentation and Performance

- Update the project README and applicable user, developer, schema, configuration, and architecture documentation in the same change when their documented behavior or contracts change.
- Document public interfaces and non-obvious constraints according to project conventions.
- Use realistic performance expectations from `ARCHITECTURE.md`; measure before adding complexity for optimization.
- Choose data structures and algorithms appropriate to expected inputs without sacrificing clarity for trivial gains.

## Working in This Codebase

Before changing code:

1. Read the approved feature record and relevant product, MVP, architecture, and design constraints.
1. Inspect surrounding code, tests, utilities, dependencies, and conventions.
1. Confirm the intended validation commands and trust boundaries.

After the final implementation pass and again after relevant review fixes:

1. Apply the focused-validation defaults and broad-suite triggers in `AGENTS.md` Efficient Execution; reuse still-current results.
1. Re-read the diff and remove unrelated or exploratory changes.
1. Update the permanent feature record with honest results.

## Quick Self-Check

- [ ] Change stays inside approved scope and preserves non-goals
- [ ] Behavior and failure handling are correct at relevant boundaries
- [ ] Names, structure, and dependencies make intent clear
- [ ] No unnecessary duplication, abstraction, dependency, or unrelated cleanup
- [ ] Data, compatibility, migration, privacy, and security promises are preserved
- [ ] Meaningful behavior and failure paths have proportionate tests
- [ ] Required validation passed or unavailable checks are recorded honestly
- [ ] Documentation and the permanent feature record match the implementation
- [ ] Final diff contains no secrets, generated clutter, or exploration leftovers

## Project-Specific Additions

Use this section only for rules that extend the universal standard: supported language/runtime versions, framework conventions, module boundaries, data-access and migration rules, testing locations, exact validation commands, or realistic platform constraints.

- [Project-specific rule]
