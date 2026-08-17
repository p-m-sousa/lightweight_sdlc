# [PROJECT_NAME] Kanban

This is the procedure of record for delivery transitions and the compact index of permanent feature records. The feature record's status is canonical; update its card and Transition History in the same change.

## Workflow

1. Confirm the exact item exists in `BACKLOG.md` and passes the Product Vision Decision Filter.
1. Classify its delivery profile, surface tags, planning route, review route, and acceptance route using `AGENTS.md`.
1. For `standard`, the primary builder prepares the smallest coherent plan. For `deep`, spawn `planner` with `fork_turns="none"` and only the root, item, profile, tags, and `pass_type=initial`. Never pass authority on a spawn; each agent definition pins its own.
1. Continue only when planning is executable and aligned. If planning is blocked, leave the item in Backlog and promptly surface only the exact missing capability or access condition. Otherwise scan `docs/features/FEAT-[0-9][0-9][0-9].md`, assign the next unused ID, create the permanent record from the template, remove the backlog row, and add a Building card.
1. If active `MVP.md` includes the item, add its feature ID and set it to Building. MVP inclusion changes still require explicit user approval.
1. Implement the approved scope in Building. Run focused validation and applicable code/design self-checks, update the project README when its documented facts changed, and record results once.
1. Spawn the mandatory read-only reviewer named by the record's review route with `fork_turns="none"`: `reviewer-standard` for `standard` and `reviewer-deep` for `deep`.
1. If review is blocked, remain in Building, record the blocked cycle, and promptly surface only the exact missing capability or access condition. Do not proceed to Testing or replace independent review with builder self-review.
1. Resolve every valid in-scope `Blocking` and `Should fix` finding. Send fixes back to the same Reviewer with `pass_type=focused-recheck`; rerun only affected validation unless a broad-suite trigger applies.
1. If standard review finds a deep trigger, update the record to `deep`, change its review route to `reviewer-deep`, and obtain focused clearance from that agent before Testing. Track findings remain non-blocking and require approval before backlog addition.
1. After clearance, move the record/card to Testing and update active MVP status when applicable.
1. For `acceptance route: independent-uat`, spawn `uat` with `fork_turns="none"` and `pass_type=initial`. For `acceptance route: builder`, the builder executes and records the same black-box cases; do not substitute source inspection for observable evidence.
1. On pass, remain in Testing and stop for human review. On blocked, remain in Testing and request only the missing environment, permission, credential, tooling, safety, or expectation decision.
1. On failure requiring project changes, return to Building, append the transition and rework cycle, make the smallest fix, rerun affected checks, and send it to the same Reviewer for focused clearance. Return to Testing and retest failed/affected cases plus the recorded core case using the same UAT agent when one exists. Rerun all feature cases only when shared behavior changed.
1. If human review finds a defect, use the same rework loop. If only evidence is missing, remain in Testing and rerun the relevant cases.
1. Move Testing to Done only after the latest acceptance verdict passes and the user explicitly approves Done. Record whether approval occurred on the first handoff, update active MVP status, and commit only when separately authorized. After every active-MVP capability reaches Done, immediately evaluate release eligibility; do not wait for another user prompt.
1. Move Building or Testing to Canceled only after explicit approval. Preserve unrelated work, record the chosen disposition, update the board and active MVP, and ask when feature changes cannot be isolated safely.
1. If all included capabilities are Done with reviewed passing acceptance, automatically enter Release Readiness below. Otherwise stop the release branch with no release record creation and continue the feature lifecycle.

Default to one Building feature. Concurrent Building work requires explicitly isolated branches or worktrees.

## Release Readiness

This is a harness process, not product work. It creates no product backlog item, feature ID, Kanban card, acceptance record, or MVP capability unless a later prepared remediation is separately authorized through the normal product/MVP/scope workflow.

1. On the automatic eligibility trigger, create `docs/releases/MVP-RELEASE.md` from `docs/releases/TEMPLATE.md` only when it does not exist; otherwise resume it. This fixed path is the one canonical harness-owned record for the active MVP. Never create a parallel or feature-owned release record.
1. Freeze the current MVP capability/checklist snapshot, map every Done approval and reviewed passing acceptance reference, record the exact claimed OS/runtime matrix, copy deterministic commands/cases from canonical documentation, and declare the core smoke check. Do not invent project evidence.
1. Generate `python3 -B .codex/scripts/context_router.py release --release docs/releases/MVP-RELEASE.md`. Continue all safe, local, no-cost work without prompting: evidence mapping, documentation consistency checks, deterministic release tooling, and applicable guarded validation. Live/network/external-side-effect or cost-bearing UAT still needs its own authorization.
1. Append a Readiness Cycle. Each stable check ID must be exactly `pending`, `pass`, `fail`, `blocked`, or `n/a` and must record its reproducible command or black-box case, date, exact environment, evidence reference, and owner/next action. Every `n/a` needs a concrete reason. Missing evidence is never a pass.
1. Ask only when the next remaining action requires a material product/MVP/design/scope decision, cost authorization, permission, credential, safety decision, destructive action, or unavailable environment. Present the exact blocked/failed check and prepared decision; do not ask the user to discover the next step.
1. For a missing product deliverable, preserve the failed check/evidence and record the smallest proposed remediation plus a recommended backlog item in Prepared Product Decisions. Create no backlog item or feature until normal scope authorization. After authorization, use the ordinary feature lifecycle, link its record from the release Rework Cycle, and resume readiness automatically after it reaches Done.
1. Never edit away failed or blocked cycles. After remediation append a Rework Cycle and a new Readiness Cycle, rerunning affected checks plus declared core smoke `RR-002`; expand only when an existing broad-suite trigger applies.
1. After RR-001 through RR-013 contain no `pending`, `fail`, or `blocked`, send the bounded Release packet to independent `reviewer-deep` with `pass_type=release-evidence`. Record its verdict as RR-014 in a new cycle. Only reviewed passing release evidence permits the builder to set Ready-for-release-review determination to Yes.
1. Keep Feature Done approval, Commit authorization, Live or cost-bearing UAT authorization, Ready-for-release-review determination, Final MVP release approval, and Publish/deploy authorization as separate fields. No field or transition implies another.
1. When the independent review passes, mark the record and `MVP.md` ready for release review, then request the user's separate explicit Final MVP release approval. Never mark the MVP Released from readiness alone, and never publish/deploy without its separate authorization.

## Board

Keep every feature link, including Done and Canceled history. Replace `None.` with a link labeled by stable feature ID and name, and move it between columns with each status change.

<table>
  <thead>
    <tr><th>Building</th><th>Testing</th><th>Done</th><th>Canceled</th></tr>
  </thead>
  <tbody>
    <tr><td>None.</td><td><a href="docs/features/FEAT-001.md">FEAT-001 Proportional In-Flight Product Refinement</a></td><td>None.</td><td>None.</td></tr>
  </tbody>
</table>
