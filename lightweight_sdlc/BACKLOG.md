# [PROJECT_NAME] Backlog

This backlog captures candidate product and technical work without letting the product drift from `PRODUCT_VISION.md`.

Backlog items normally have no feature ID. When an item enters Building, the builder follows `KANBAN.md`, assigns the next unused `FEAT-XXX` ID, and creates one permanent record under `docs/features/`.

When `MVP.md` is active, it is the sole source of MVP inclusion. Do not add a duplicate MVP flag or milestone column here.

## Rating Method

`score = usefulness - complexity + 3`

- Usefulness: 1 low, 5 high.
- Complexity: 1 easy, 5 hard.
- Score: 1 low priority, 7 highest priority.

## Feature Backlog

| Feature Idea | Usefulness | Complexity | Score | Notes |
| --- | ---: | ---: | ---: | --- |
| [Feature idea] | [1-5] | [1-5] | [1-7] | [User value, smallest useful version, and product constraints.] |

**EXAMPLE ONLY:**

| Feature Idea | Usefulness | Complexity | Score | Notes |
| --- | ---: | ---: | ---: | --- |
| Restore from backup | 5 | 3 | 5 | Validate and preview a chosen backup before confirmed replacement; avoid general file management. |

## Parking Lot

Use this section for ideas that are not aligned enough for active grooming.

| Idea | Reason |
| --- | --- |
| [Idea] | [Current conflict or condition required before reconsideration.] |

**EXAMPLE ONLY:**

| Idea | Reason |
| --- | --- |
| Social community features | Conflicts with a private, user-controlled direction unless the product vision changes. |

## Technical Enhancement Backlog

Add technical, quality, accessibility, maintainability, performance, or test improvements only after explicit user approval.

| Priority | Enhancement | Why It Matters |
| ---: | --- | --- |
| 1 | [Technical enhancement] | [How it makes the product safer, more reliable, or easier to maintain.] |

**EXAMPLE ONLY:**

| Priority | Enhancement | Why It Matters |
| ---: | --- | --- |
| 1 | Introduce typed storage and schema migrations | Protects user data as schemas evolve. |
