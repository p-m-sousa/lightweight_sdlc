# DESIGN_SYSTEM.md

This file is the source of truth for user-facing design quality. `PRODUCT_VISION.md` defines direction and trust; this file turns that direction into consistent, accessible interface rules. When they conflict, the product vision wins and this file must be reconciled.

The goal is an interface that is clear, consistent, accessible, intentional, and faithful to the product's approved feel.

## 1. Principles

- Reuse established tokens, components, and platform patterns before inventing a local solution.
- Make actions, hierarchy, state, and consequences understandable without instructions.
- Let product direction determine aesthetic choices, density, and motion rather than applying a universal style.
- Build accessibility into the initial implementation.
- Use progressive disclosure for complexity and honor the product's privacy, ownership, sharing, and permission promises.

## 2. Tokens and Foundations

Define only the tokens the product needs and reference them by role rather than appearance.

- Color: background, surface, text, border, accent, and applicable semantic roles. Verify WCAG AA contrast; never judge it by eye.
- Typography: approved font stack, type scale, weights, and line heights. Support dynamic type or zoom without clipping.
- Spacing and layout: a small spacing scale, content widths, safe margins, and breakpoints where applicable.
- Shape and depth: a small radius, border, and elevation system with consistent meaning.
- Motion: a few durations and easing curves tied to clear purposes, with reduced-motion alternatives.
- Themes: components use semantic roles so every supported theme receives equivalent behavior and contrast.

Avoid hard-coded component values when an established token represents the decision.

## 3. Components and Interaction

For each reusable component, define its purpose, variants, states, and usage limits. Standardize only components the product actually uses.

- Make action hierarchy clear and follow the project-specific limit on primary actions.
- Give interactive elements visible focus, accessible names, and platform-appropriate target sizes.
- Explain unavailable actions when that knowledge helps the user; do not rely on a greyed-out appearance alone.
- Avoid stacking dialogs or inventing navigation patterns when the platform convention works.
- Use icons without visible text only when context makes the action clear; always provide an accessible label.
- Introduce reusable tokens, components, or patterns here rather than as one-off UI tweaks.

## 4. Required States

Design every state the changed surface can realistically enter:

- Empty: explain what belongs there and provide a useful next step.
- Loading: communicate the wait without unnecessarily blocking available content.
- Error: use plain language, preserve useful context, and offer recovery when possible.
- Success: match feedback prominence to the importance of the action.
- Partial or offline: show usable content and clearly identify what is unavailable.
- Destructive or permission-sensitive: explain the consequence and require confirmation when the trust promise demands it.

## 5. Voice and Content

- Match the tone, terminology, and casing approved in the product-specific additions.
- Use the audience's language and describe outcomes rather than implementation details.
- Make labels and errors specific; buttons should state the result of the action.
- Never expose raw codes or stack traces as the only user-facing explanation.
- Treat empty, error, permission, destructive, and recovery copy as part of the design.

## 6. Accessibility and Platform Behavior

- Meet WCAG AA contrast: 4.5:1 for body text, 3:1 for large text, and 3:1 for meaningful non-text UI.
- Never use color as the only signal.
- Provide logical focus and reading order, visible focus indicators, explicit form labels, and accessible names.
- Respect screen readers, keyboard or switch input, dynamic type/zoom, reduced motion, and high-contrast settings supported by the platform.
- Use platform-recommended touch or pointer targets and test the smallest supported viewport or device size.
- Follow platform conventions unless a documented product-specific reason justifies a departure.

## Working in This Design System

Before user-facing work:

1. Read `PRODUCT_VISION.md`, this file, the approved feature record, and relevant prior surfaces.
1. Check `UI_TWEAKS.md` and linked Done feature records only when they contain applicable visual decisions.
1. Reuse existing tokens, components, states, and platform behavior.

Before review and again after review fixes, run the self-check and record the result in the permanent feature record. A design-system storyboard is optional and should be created only after explicit user approval when visual token review would materially help.

## Quick Self-Check

- [ ] Supports the approved product direction and trust promise
- [ ] Reuses applicable tokens, components, and platform patterns
- [ ] Has clear hierarchy, actions, consequences, and recovery
- [ ] Covers relevant empty, loading, error, success, partial, and destructive states
- [ ] Meets contrast, non-color signaling, naming, focus, and target-size requirements
- [ ] Works with relevant screen reader, keyboard/switch, dynamic type/zoom, and reduced-motion settings
- [ ] Uses specific, consistent copy and approved terminology/casing
- [ ] Works at the smallest supported size and in every supported theme
- [ ] Adds reusable design decisions here rather than as one-off values
- [ ] Permanent feature record contains honest validation results

## Project-Specific Additions

Define only concrete rules needed by this product: aesthetic intent, density, palette and accents, typography, spacing, shape, motion, casing, action hierarchy, platform targets, themes, and product-specific components or state patterns.

- [Project-specific design rule]
