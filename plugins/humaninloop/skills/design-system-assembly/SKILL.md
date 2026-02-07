---
name: design-system-assembly
description: >
  This skill MUST be invoked when the user says "assemble design system",
  "build design system", "merge extractions", "consolidate tokens",
  "unify design tokens", or "synthesize design system". SHOULD also invoke
  when user mentions "design system", "token consolidation", "component
  normalization", or "multi-screenshot synthesis".
---

# Design System Assembly

## Overview

Synthesize individual screenshot extractions produced by `humaninloop:screenshot-analysis` into a unified, coherent design system. Every token in the final system traces back to its source screenshot, every conflict is documented with resolution rationale, and the output is implementation-ready.

## When to Use

- Multiple screenshot extractions exist and need merging into one system
- Token consolidation required across color, typography, spacing, and elevation
- Component variants from different sources need harmonizing
- Building a unified design system from visual inspiration across apps
- Preparing implementation-ready token definitions from merged extractions

## When NOT to Use

- Only one screenshot extraction exists (no merging needed -- use the extraction directly)
- Designing from scratch without reference screenshots (use `humaninloop:patterns-interface-design`)
- Extractions have not been completed yet (run `humaninloop:screenshot-analysis` first)
- Implementing an already-defined design system (no synthesis needed)

## Prerequisites

**REQUIRED:** Run `humaninloop:screenshot-analysis` on each reference screenshot before invoking this skill. Each extraction provides the raw material for assembly.

Gather all extraction documents. Each extraction should contain: color palette, typography scale, spacing scale, component catalog, layout structure, and border/elevation system.

## Phase 1: Extraction Inventory

Before merging anything, catalog what exists.

### Process

1. List every extraction by source name (e.g., "Linear dashboard," "Stripe checkout," "Notion sidebar")
2. For each extraction, note what token categories are present and what is marked as a gap
3. Identify overlap -- which categories appear in multiple extractions
4. Identify unique contributions -- tokens or components present in only one source

### Output Format

```
EXTRACTION INVENTORY

Source 1: [Name]
  Platform: [platform]
  Color tokens: [count] | Typography levels: [count] | Spacing values: [count]
  Components: [list]
  Gaps: [list]

Source 2: [Name]
  ...

OVERLAP MATRIX:
  Colors:      Sources [1, 2, 3] — merge required
  Typography:  Sources [1, 3] — merge required
  Spacing:     Sources [1, 2] — merge required
  Components:  Sources [1, 2, 3] — normalization required
  Elevation:   Source [2] only — adopt directly

UNIQUE CONTRIBUTIONS:
  Source 1: [specific tokens or components only this source provides]
  Source 2: [specific tokens or components only this source provides]
```

## Phase 2: Token Consolidation

Merge color palettes, typography scales, and spacing scales from all sources into unified scales.

### Color Consolidation

1. **Collect all neutrals** -- List every background, surface, border, and text color from every source. Group by role (background-base, background-elevated, text-primary, etc.).
2. **Identify near-duplicates** -- Colors within delta-E 3.0 of each other serving the same role are candidates for merging. Choose the value that best serves the intended palette temperature.
3. **Resolve conflicts** -- When two sources assign different colors to the same role (e.g., different background-base values), document both and select one. Record the rationale.
4. **Build unified palette** -- Assign every color a single canonical name. Attribute each to its source.

```
UNIFIED COLOR PALETTE

NEUTRALS:
  bg-base:       #1A1A2E  (from: Source 1 — Notion dark mode)
  bg-elevated:   #222240  (from: Source 2 — Linear cards)
  bg-surface:    #2A2A4A  (derived: midpoint between Source 1 and Source 2)
  ...

CONFLICTS RESOLVED:
  bg-base: Source 1 used #1A1A2E, Source 2 used #1C1C1C
  Decision: Adopted Source 1 value — warmer tone aligns with brand direction
```

### Typography Consolidation

1. **Align scales** -- Map each source's type levels to a common naming convention (display, h1, h2, h3, body, caption, label, overline).
2. **Resolve size conflicts** -- When sources disagree on a level's size, favor the value from the source whose overall scale has better mathematical consistency (e.g., major third ratio).
3. **Unify font families** -- Select one primary, one monospace. Document alternatives considered.
4. **Unify weights** -- Build a single weight scale covering all needed weights across sources.

### Spacing Consolidation

1. **Identify base units** -- Note each source's base unit (4px, 8px, etc.).
2. **Standardize** -- Choose one base unit. If sources disagree, prefer the value that produces the most consistent scale.
3. **Merge scales** -- Combine all spacing values into a single scale. Eliminate redundant values within 1px of each other.
4. **Validate coverage** -- Ensure the unified scale covers micro (2-4px), component (8-16px), section (24-48px), and layout (64px+) ranges.

## Phase 3: Component Normalization

Harmonize component variants from different sources into a consistent library.

### Process

1. **Build a component union** -- List every component type that appears in any extraction.
2. **Merge variants** -- For components that appear in multiple sources, merge variant lists. Remove duplicates.
3. **Retoken components** -- Replace each component's original color, spacing, and typography references with the unified tokens from Phase 2.
4. **Resolve style conflicts** -- When sources use different border-radii, padding, or styling for the same component type, document the options and choose one.
5. **Assign component tokens** -- Each component references only unified system tokens. No hard-coded values.

### Output Format

```
COMPONENT: Button
  Sources: [Source 1, Source 3]
  Variants: primary, secondary, ghost, icon-only
  Resolved tokens:
    Height: var(--space-xl) (40px)
    Padding: var(--space-xs) var(--space-md)
    Border radius: var(--radius-md)
    Font: var(--font-size-label) / var(--font-weight-medium)
    Colors:
      Primary BG: var(--color-brand-primary)
      Primary text: var(--color-text-inverse)
      Secondary BG: var(--color-bg-elevated)
  Conflict notes:
    Source 1 used 8px radius, Source 3 used 12px.
    Decision: 8px — matches the overall compact density.
```

## Phase 4: Hierarchy Establishment

Define primary/secondary/tertiary relationships across the entire system.

### Color Hierarchy

| Level | Purpose | Example Assignment |
|-------|---------|-------------------|
| Primary | Main actions, brand expression | Brand color for buttons, links |
| Secondary | Supporting actions, alternative paths | Muted brand for secondary buttons |
| Tertiary | Background accents, hover states | Tinted surfaces |
| Neutral | Content, structure, text | Gray scale for text and borders |
| Semantic | Status communication | Success, warning, error, info |

### Typography Hierarchy

| Level | Role | Tokens |
|-------|------|--------|
| Display | Hero content, landing sections | Largest size, heaviest weight |
| Heading | Section titles, page headers | h1 through h3 |
| Body | Primary content, descriptions | Standard reading size |
| UI | Labels, buttons, inputs | Slightly smaller, medium weight |
| Caption | Metadata, timestamps, help text | Smallest, muted color |

### Spacing Hierarchy

| Context | Scale Range | Application |
|---------|-------------|-------------|
| Component internals | 2xs through sm | Icon gaps, input padding, tight pairs |
| Between elements | sm through lg | Form fields, button groups, list items |
| Section separation | lg through 2xl | Content sections, card groups |
| Layout structure | 2xl through 3xl | Page margins, major divisions |

## Phase 5: Conflict Resolution

All conflicts identified during Phases 2-4 MUST be documented in a single conflict log.

### Conflict Log Format

```
CONFLICT LOG

ID: C-001
Category: Color
Description: Background base color differs between sources
  Source 1: #1A1A2E (warm dark blue)
  Source 2: #1C1C1C (neutral dark gray)
Resolution: Adopted #1A1A2E
Rationale: Warm undertone creates more inviting feel; neutral gray reserved
  for elevated surfaces to create natural contrast hierarchy.

ID: C-002
Category: Spacing
Description: Base unit differs between sources
  Source 1: 4px base
  Source 3: 8px base
Resolution: Adopted 8px base
Rationale: 8px produces fewer fractional values at standard component sizes;
  4px granularity available through 0.5x multiplier where needed.
```

Mark every conflict with a unique ID. Reference these IDs in the final system documentation when a token's origin involves a resolved conflict.

## Phase 6: System Documentation

Produce the final design system document.

### Required Sections

1. **System Overview** -- Name, purpose, sources, design philosophy
2. **Color System** -- Full palette organized by role, with source attribution
3. **Typography System** -- Font families, type scale, weight scale, line heights
4. **Spacing System** -- Base unit, full scale, usage guidelines
5. **Border and Elevation** -- Radii, shadows, border treatments, depth strategy
6. **Component Library** -- Each component with tokens, variants, and states
7. **Source Attribution Index** -- Every token traced to its origin screenshot
8. **Conflict Resolution Log** -- Full log from Phase 5
9. **Known Gaps** -- Aggregated gaps from all extractions plus assembly-stage gaps

### Source Attribution Index Format

```
SOURCE ATTRIBUTION INDEX

Token                    Source          Conflict?
──────────────────────── ─────────────── ─────────
--color-brand-primary    Source 1        No
--color-bg-base          Source 1        C-001
--color-bg-elevated      Source 2        No
--font-family-primary    Source 1        No
--space-base             Source 3        C-002
--radius-md              Source 1        C-003
```

## Phase 7: Implementation Mapping

Translate the unified system into code-ready formats. See [references/implementation-output-templates.md](references/implementation-output-templates.md) for complete templates.

### Required Outputs

Produce at least ONE of the following based on the target platform:

| Platform | Output |
|----------|--------|
| Web (vanilla) | CSS custom properties on `:root` |
| Web (Tailwind) | `tailwind.config.js` theme extension |
| iOS | SwiftUI `DesignTokens` enum |
| Android | Compose `Theme.kt` tokens |
| Cross-platform | All applicable formats |

### Mapping Rules

- Every token in the implementation MUST reference the system documentation name
- Comments in code MUST include the source attribution (e.g., `/* from: Linear dashboard */`)
- Tokens not observed in any screenshot MUST NOT be fabricated -- leave placeholders explicit
- Group tokens by category matching the system documentation structure

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Merging colors without checking delta-E proximity | Compare colors numerically; near-duplicates within delta-E 3.0 should merge |
| Dropping source attribution during consolidation | Carry attribution through every phase; final system traces every token to a screenshot |
| Choosing one source's tokens wholesale and ignoring others | Evaluate each token category independently; best values may come from different sources |
| Resolving conflicts without documenting rationale | Every conflict resolution needs a written justification in the conflict log |
| Creating components with hard-coded values instead of system tokens | Every component value must reference a unified token; no magic numbers |
| Skipping the gaps section because "the system is complete" | Aggregate gaps from all extractions; assembly introduces additional gaps (e.g., untested combinations) |
| Producing implementation code without source comments | Code-level comments connect tokens back to design decisions and source screenshots |
| Treating spacing from different sources as additive instead of deduplicating | Merge overlapping values; the unified scale should be smaller than the sum of all source scales |

## Quality Checklist

Before delivering the assembled design system:

**Inventory:**
- [ ] All source extractions cataloged with platform and token counts
- [ ] Overlap matrix identifies merge points
- [ ] Unique contributions from each source noted

**Consolidation:**
- [ ] Color palette unified with roles assigned and near-duplicates merged
- [ ] Typography scale uses consistent naming and mathematical ratios
- [ ] Spacing scale has a single base unit with full range coverage
- [ ] Border radii and shadow values unified

**Normalization:**
- [ ] Every component uses unified system tokens only (no hard-coded values)
- [ ] Component variant lists merged across sources
- [ ] Style conflicts resolved and documented

**Hierarchy:**
- [ ] Color hierarchy (primary through semantic) established
- [ ] Typography hierarchy (display through caption) defined
- [ ] Spacing hierarchy (component through layout) mapped

**Transparency:**
- [ ] Every token has source attribution
- [ ] Conflict log covers all disagreements between sources
- [ ] Known gaps aggregated from all extractions
- [ ] No fabricated values for unobserved properties

**Implementation:**
- [ ] At least one code-ready output produced
- [ ] Code comments include source attribution
- [ ] Token names in code match system documentation names
