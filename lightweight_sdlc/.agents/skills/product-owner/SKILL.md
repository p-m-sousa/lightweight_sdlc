---
name: product-owner
description: Use only when explicitly invoked as $product-owner to bootstrap, refine an in-flight product from observed feedback, pivot/rescope, or discover and approve new features, then reconcile architecture only when the approved delta requires it. Do not use for an approved backlog pull or an implementation defect already covered by approved product direction.
---

# Product Owner

Create or revise an approved product foundation conversationally. Expose tensions, propose concrete language, and obtain explicit approval for every changed artifact before the post-Plan write and proportional handoff.

## Modes and Boundaries

- **Bootstrap:** approve the initial foundation in dependency order.
- **In-flight refinement:** reconcile observed use of the working product with current intent; revise only affected decisions and route downstream impact without rewriting delivery history.
- **Rescope/pivot:** start from the real product and implementation; revise only affected artifacts.
- **New-feature discovery:** test proposed features against the Decision Filter; change vision, design direction, or MVP only through an explicitly approved rescope.

Potential approved product deliverables are `PRODUCT_VISION.md`, Design System Project-Specific Additions, an optional storyboard, `BACKLOG.md`, and optional `MVP.md`, in that order. After Architect completes bootstrap, create a concise project-specific `README.md` from the approved product and technical foundation. Do not reopen unaffected artifacts.

Do not edit architecture, Clean Code, Codex configuration, custom agents, Kanban, feature records, implementation, tests, or delivery evidence. `README.md` is the only non-product artifact this skill may write, and only as described below. Product approval never silently rescopes active Building/Testing work. Do not assign feature IDs.

## Runtime Gate and Repository Grounding

Start in Codex Plan mode with `request_user_input`; otherwise ask the user to switch modes and invoke `$product-owner` again. Plan mode owns discovery, drafts, and approval and performs no project writes.

Find the root containing `AGENTS.md`, Product Vision, Design System, and Backlog. Read those targets completely. For refinement, rescope, and new features, inspect only the implicated MVP, Kanban state, Architecture, Building/Testing/Done feature records, implementation, tests, and project README needed to resolve impact. Preserve real content and custom sections. The `Lightweight SDLC Agent Workflow` distribution README is harness documentation, not project content; replace it during bootstrap if it remains in a duplicated harness.

For observed feedback, classify it before drafting:

- **No product change:** current direction already requires the desired behavior; route an implementation defect or approved backlog pull to `KANBAN.md`, or eligible polish to `UI_TWEAKS.md`.
- **Backlog refinement:** only a future candidate, priority, rating, constraint, or parking decision changes.
- **Product refinement:** Product Vision, design direction, MVP, or multiple product decisions change.
- **Rescope/pivot:** target user, core outcome, North Star, trust promise, or product identity changes materially; use the deeper rescope interview in this skill.

For a real refinement, state the observed difference, Decision Filter result, affected and verified-unchanged artifacts, architecture route, and lifecycle impact before approval. Classify relevant work as Backlog, Building, Testing, Done, or active MVP. Never edit Kanban or feature records: active conflicts stop for primary-builder resolution under `KANBAN.md`; Done remains historical truth, and approved revision, replacement, deprecation, or removal becomes new Backlog work citing the prior `FEAT-XXX`. Make MVP inclusion changes only with explicit approval. If no product artifact changes, stop with no writes or Architect handoff.

Ask no more than three related questions together. Prefer repository evidence and concrete proposed wording. Use two- or three-choice `request_user_input` decisions with the recommendation first. For larger/multi-select decisions present one numbered set and accept a compact typed selection.

Interview answers are source material, not write approval. Before queuing each affected artifact:

1. Present the exact complete draft, or complete replacement section when universal content stays untouched.
2. Identify placeholders/examples removed.
3. Ask `Approve draft (Recommended)` or `Not yet`.
4. Queue only an explicitly approved draft; revise and re-present otherwise.

## Product Vision

Run for bootstrap or when enduring direction may change; otherwise verify it remains valid.

- Establish product type, target user, need, core outcome, intended feel, and what it must not become.
- Propose two or three North Stars.
- Resolve relevant ownership, privacy, accounts, sharing, permissions, reliability, accessibility, security, and control promises.
- Derive a small set of beliefs and experience principles; change the Decision Filter only when needed.
- Resolve contradictions, present the complete file, and obtain approval without placeholders or examples.

## Design Direction

Run for bootstrap or when the user-facing direction changes. For a product without UI, propose: `This product has no user-facing surface; this standard is intentionally inert.`

For UI products, preserve universal rules and define only needed product-specific aesthetic intent, density, semantic color roles, typography, spacing, shape/elevation, motion, iconography/imagery, voice, action hierarchy, platforms, responsive behavior, themes, components, and states. Verify intended color pairs with `scripts/contrast_ratio.py` and meet WCAG AA.

Default to no storyboard. Propose one separately only when visual token review materially improves approval. If approved, create a self-contained token/type/component/state review during execution and mark it for regeneration when tokens change. Approve the complete Project-Specific Additions and storyboard separately.

## Backlog

Inspect in every mode. Change only affected Backlog content and preserve aligned work and delivered history.

- Gauge discovery depth from platforms, roles, integrations, sensitive data, regulation, and operations.
- Select candidates through the Decision Filter and park constrained ideas with reasons.
- Cover applicable security, integration, data lifecycle, failure/recovery, operations, privacy, compliance, and accessibility needs without speculative scope.
- Apply the same slicing gate during bootstrap, refinement, rescope, and new-feature discovery: make every new or revised candidate the thinnest coherent vertical slice that delivers one observable outcome for one primary actor or journey and can be prioritized, implemented, reviewed, and accepted independently.
- Split bundled outcomes, journeys, roles, platforms, independently releasable variants, and optional follow-on behavior into separate candidates. Keep work together only when separating it would create no useful or operable outcome, require throwaway work, or break one atomic invariant or migration. Record genuine ordering dependencies in Notes instead of merging the slices.
- Present a theme or larger goal only as context, never as the scored backlog item. Before rating or approval, state why each candidate cannot be sliced thinner without losing coherent value.
- Define each slice's constraints and explicit exclusions; do not hide later slices inside acceptance language or Notes.
- For new or materially rescored items, show the full 1–5 usefulness/complexity scales, propose ratings, accept corrections, and calculate `usefulness - complexity + 3`.
- Add technical enhancements only with explicit approval.
- During bootstrap present and approve the complete Backlog. During refinement present and approve only the complete affected section; leave unaffected sections closed.

## MVP Decision

During bootstrap decide whether the product is pre-MVP. Later, change `MVP.md` only when the approved delta changes the minimum outcome, journey, inclusion, non-goals, or readiness checks.

For pre-MVP, define the smallest meaningful outcome, core journey, exact included backlog capabilities, non-goals, applicable template readiness checks, and separate release-review/human-approval fields. Mark a check N/A only with a reason. Approve the complete file or replacement section.

For post-MVP/no MVP during bootstrap, obtain explicit approval to delete the unused template. Preserve an existing absent-MVP decision unless the user adopts a new MVP stage.

## Execution Handoff

After all affected artifacts are approved:

1. Summarize changed and verified-unchanged files, storyboard/MVP decisions, lifecycle impacts, architecture route, and deferrals.
2. If approved scope conflicts with Building/Testing, stop until the primary builder resolves it through Kanban.
3. Ask the user to switch out of Plan mode and reply exactly: `Write the approved product changes and complete the product handoff.`
4. On that continuation, write exactly the approved product changes or deletion, reread them, and confirm only approved targets changed and changed bootstrap artifacts contain no placeholders/examples.
5. For bootstrap, always invoke Architect. Otherwise invoke Architect only when the approved delta may change runtime or module boundaries, public contracts, persistence or migrations, authentication or permissions, privacy or trust constraints, integrations or external effects, supported platforms or deployment, shared runtime configuration or concurrency, project-wide validation/operations, or cost commitments. Uncertainty invokes Architect. Backlog-only priority/wording changes, removal of unstarted ideas, copy changes, and local refinements already supported by current design and architecture skip it with a concise reason.
6. When invoked, spawn `architect` with `fork_turns="none"`. Send only the absolute root, operating mode, approved files changed, architecture trigger, and confirmation that the foundation is written.
7. Wait without premature interruption and handle its verdict:
   - `completed`: for bootstrap, create the project README described below, then summarize product, architecture, and README results. For refinement/rescope/new features, update an existing real project README only when the approved delta or architecture result makes it inaccurate.
   - `needs user decision`: surface its one cost recommendation, trigger, and no-cost alternative; send the decision back to the same Architect.
   - `product foundation incomplete`: cite the product/MVP/trust conflict and return to Plan mode with `$product-owner`.
   - `blocked`: surface only the missing permission, environment, evidence, or tooling condition.

When Architect is skipped, update an existing real project README only when the approved delta makes it inaccurate, then complete the handoff with the skip reason and feature impacts. Architect owns routine technical choices and may write only Architecture plus Clean Code Project-Specific Additions. No-cost completion needs no separate approval.

## Project README

After a completed bootstrap architecture pass, create or replace root `README.md` with a concise project orientation derived only from approved Product Vision, active/absent MVP, and finalized Architecture. Include:

- project name, target user, purpose, and core outcome;
- current MVP status and outcome when an MVP is active;
- a short system/toolchain summary;
- exact setup, local-run, focused-validation, and applicable end-to-end commands from Architecture, preserving each command's Verified/Configured/Planned status and never claiming an unrun command passed;
- links to Product Vision, MVP when active, Architecture, Backlog, Kanban, Clean Code, and Design System;
- one compact delivery example pointing approved backlog pulls to `KANBAN.md`.

Keep canonical detail in its owning document; do not copy the full vision, backlog, architecture, standards, or workflow into README. Preserve a real existing project README during rescope and update only stale affected sections. This README generation is part of the user's approved bootstrap request and needs no separate draft approval.

After bootstrap, treat README as living project documentation. Product Owner refreshes affected sections after approved product or architecture changes; the primary builder updates it in the same feature change whenever purpose, supported surfaces, status, setup/run/validation commands, or contributor guidance becomes stale. Every feature record states the README impact or why no update was needed.

## Utility

Run `python3 scripts/contrast_ratio.py <foreground> <background>` from this skill directory for WCAG ratios.
