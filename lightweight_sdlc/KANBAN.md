# [PROJECT_NAME] Kanban

This is the procedure of record for delivery transitions and the compact index of permanent feature records. The feature record's status is canonical; update its card and Transition History in the same change.

## Workflow

1. Confirm the exact item exists in `BACKLOG.md` and passes the Product Vision Decision Filter.
1. Classify its delivery profile, surface tags, planning route, review route, and acceptance route using `AGENTS.md`.
1. For `standard`, the primary builder prepares the smallest coherent plan. For `deep`, spawn `planner` with `fork_turns="none"`, Terra Medium, and only the root, item, profile, tags, and `pass_type=initial`.
1. Continue only when planning is executable and aligned. If planning is blocked, leave the item in Backlog and promptly surface only the exact missing capability or access condition. Otherwise scan `docs/features/FEAT-[0-9][0-9][0-9].md`, assign the next unused ID, create the permanent record from the template, remove the backlog row, and add a Building card.
1. If active `MVP.md` includes the item, add its feature ID and set it to Building. MVP inclusion changes still require explicit user approval.
1. Implement the approved scope in Building. Run focused validation and applicable code/design self-checks, update the project README when its documented facts changed, and record results once.
1. Spawn the mandatory read-only `reviewer` with `fork_turns="none"`. Use Terra High for `standard` and Sol High for `deep`.
1. If review is blocked, remain in Building, record the blocked cycle, and promptly surface only the exact missing capability or access condition. Do not proceed to Testing or replace independent review with builder self-review.
1. Resolve every valid in-scope `Blocking` and `Should fix` finding. Send fixes back to the same Reviewer with `pass_type=focused-recheck`; rerun only affected validation unless a broad-suite trigger applies.
1. If standard review finds a deep trigger, update the record to `deep` and obtain focused Sol-High clearance from the same Reviewer before Testing. Track findings remain non-blocking and require approval before backlog addition.
1. After clearance, move the record/card to Testing and update active MVP status when applicable.
1. For `acceptance route: independent-uat`, spawn `uat` with `fork_turns="none"`, Terra Medium, and `pass_type=initial`. For `acceptance route: builder`, the builder executes and records the same black-box cases; do not substitute source inspection for observable evidence.
1. On pass, remain in Testing and stop for human review. On blocked, remain in Testing and request only the missing environment, permission, credential, tooling, safety, or expectation decision.
1. On failure requiring project changes, return to Building, append the transition and rework cycle, make the smallest fix, rerun affected checks, and send it to the same Reviewer for focused clearance. Return to Testing and retest failed/affected cases plus the recorded core case using the same UAT agent when one exists. Rerun all feature cases only when shared behavior changed.
1. If human review finds a defect, use the same rework loop. If only evidence is missing, remain in Testing and rerun the relevant cases.
1. Move Testing to Done only after the latest acceptance verdict passes and the user explicitly approves Done. Record whether approval occurred on the first handoff, update active MVP status, and commit only when authorized.
1. Move Building or Testing to Canceled only after explicit approval. Preserve unrelated work, record the chosen disposition, update the board and active MVP, and ask when feature changes cannot be isolated safely.
1. When every active MVP capability is Done and release checks pass, mark it ready for release review and ask for separate release approval.

Default to one Building feature. Concurrent Building work requires explicitly isolated branches or worktrees.

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
