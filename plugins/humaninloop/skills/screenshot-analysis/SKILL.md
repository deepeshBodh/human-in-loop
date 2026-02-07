---
name: screenshot-analysis
description: >
  This skill MUST be invoked when the user says "analyze screenshot",
  "extract design tokens", "pull colors from screenshot", "component inventory",
  "break down this UI", or "design extraction". SHOULD also invoke when user
  mentions "screenshot", "color palette", "typography", "spacing", or
  "component catalog".
---

# Screenshot Analysis

## Overview

Extract precise, implementation-ready design tokens, components, and layout structure from screenshot images through a systematic eight-phase process. Every extraction must trace back to something observed in the screenshot, and every gap must be explicitly acknowledged.

## When to Use

- Analyzing a screenshot image to extract a design system
- Building a color palette from an existing interface
- Cataloging components visible in a UI screenshot
- Identifying typography scale and hierarchy from a reference app
- Measuring spacing patterns and grid structure from a screenshot
- Producing implementation-ready tokens from visual inspiration

## When NOT to Use

- Designing from scratch without reference screenshots
- Working from design files (Figma, Sketch) where tokens are already exported
- Pure interaction design without visual analysis
- When the user provides a design system spec and needs implementation only

## Phase 1: Initial Assessment

Before extracting any tokens, establish the context of the interface.

**Identify and document:**

| Attribute | What to Determine |
|-----------|-------------------|
| Platform | Mobile (iOS/Android), web (desktop/responsive), desktop app |
| Design language | Material, iOS HIG, custom, hybrid |
| Layout approach | Single column, multi-column, sidebar+content, dashboard grid |
| Density | Compact (data-heavy), comfortable (standard), spacious (marketing) |
| Color mode | Light, dark, or mixed |
| Apparent era | Current design trends vs. dated patterns |

**Output format:**
```
PLATFORM: [platform]
DESIGN LANGUAGE: [language]
LAYOUT: [approach]
DENSITY: [level]
COLOR MODE: [mode]
NOTES: [anything notable about the overall approach]
```

## Phase 2: Color Extraction

Extract every distinguishable color. Organize by role, not by where it appears.

### Extraction Process

1. **Backgrounds first** -- Identify every distinct background color. Number them from darkest to lightest (or lightest to darkest in dark mode).
2. **Text colors** -- Identify primary text, secondary text, muted/placeholder text, and any colored text.
3. **Interactive elements** -- Buttons, links, toggles, active states. Separate primary actions from secondary.
4. **Semantic colors** -- Success (green), warning (amber/yellow), error/destructive (red), info (blue). Note which are present and which are absent.
5. **Accent and brand** -- The dominant brand color. Any secondary accent.
6. **Borders and dividers** -- Often subtle. Zoom in mentally. Note opacity if borders appear semi-transparent.

### Output Format

```
PRIMARY PALETTE:
  Brand Primary:    #XXXXXX  (observed in: [element])
  Brand Secondary:  #XXXXXX  (observed in: [element])

NEUTRAL PALETTE:
  Background Base:  #XXXXXX  (observed in: [element])
  Background Elevated: #XXXXXX  (observed in: [element])
  Surface:          #XXXXXX  (observed in: [element])
  Border Default:   #XXXXXX  (observed in: [element])
  Text Primary:     #XXXXXX  (observed in: [element])
  Text Secondary:   #XXXXXX  (observed in: [element])
  Text Muted:       #XXXXXX  (observed in: [element])

SEMANTIC PALETTE:
  Success:          #XXXXXX  (observed in: [element])
  Warning:          #XXXXXX  (observed in: [element])
  Error:            #XXXXXX  (observed in: [element])
  Info:             #XXXXXX  (observed in: [element])

ACCENT PALETTE:
  [role]:           #XXXXXX  (observed in: [element])
```

Every color entry MUST include the `(observed in: ...)` attribution. If a semantic color is not visible in the screenshot, omit it and note its absence in the gaps section.

## Phase 3: Typography Identification

Identify every distinct typographic treatment visible in the screenshot.

### Extraction Process

1. **Scan top to bottom** -- Note every text element, grouping by apparent visual hierarchy level.
2. **Font family** -- Identify the typeface. If uncertain, provide the closest match (e.g., "appears to be Inter or similar geometric sans-serif").
3. **Size scale** -- Measure relative sizes. Anchor to body text and express other sizes as ratios or estimated pixel values.
4. **Weight scale** -- Note distinct weights visible (regular, medium, semibold, bold).
5. **Line height** -- Estimate for body text and headings. Note whether headings use tighter line height than body.
6. **Letter spacing** -- Note any visible tracking differences (tight headings, wider labels, uppercase with extra tracking).
7. **Special treatments** -- Monospace for code, tabular numbers for data, italic for emphasis.

### Output Format

```
FONT FAMILIES:
  Primary:    [family] (confidence: high/medium/low)
  Secondary:  [family] (confidence: high/medium/low)
  Monospace:  [family] (if present)

TYPE SCALE:
  Display:    ~[size]px / weight [N] / leading [N] (observed in: [element])
  Heading 1:  ~[size]px / weight [N] / leading [N] (observed in: [element])
  Heading 2:  ~[size]px / weight [N] / leading [N] (observed in: [element])
  Heading 3:  ~[size]px / weight [N] / leading [N] (observed in: [element])
  Body:       ~[size]px / weight [N] / leading [N] (observed in: [element])
  Caption:    ~[size]px / weight [N] / leading [N] (observed in: [element])
  Label:      ~[size]px / weight [N] / leading [N] (observed in: [element])
  Overline:   ~[size]px / weight [N] / leading [N] (observed in: [element])

LETTER SPACING:
  Headings: [value or "normal"]
  Labels:   [value or "normal"]
  Overline: [value or "normal"]
```

Mark all pixel values with `~` (approximate) unless the screenshot provides enough context for exact measurement. Note confidence level for font family identification.

## Phase 4: Spacing Measurement

Extract the spacing system by identifying the base unit and its multipliers.

### Extraction Process

1. **Find the base unit** -- Examine the smallest repeated spacing value. Common bases: 4px, 8px. Look at icon-to-text gaps, input padding, and tight element pairs.
2. **Internal component spacing** -- Padding inside buttons, cards, inputs, list items.
3. **Between-element spacing** -- Gaps between sibling elements (button groups, form fields, list items).
4. **Section spacing** -- Distance between major content sections.
5. **Page margins** -- Outer padding of the main content area.
6. **Consistent vs. inconsistent** -- Note whether spacing follows a strict scale or varies.

### Output Format

```
BASE UNIT: [N]px

SPACING SCALE:
  2xs:  [N]px  ([base] x [multiplier]) — used for: [context]
  xs:   [N]px  ([base] x [multiplier]) — used for: [context]
  sm:   [N]px  ([base] x [multiplier]) — used for: [context]
  md:   [N]px  ([base] x [multiplier]) — used for: [context]
  lg:   [N]px  ([base] x [multiplier]) — used for: [context]
  xl:   [N]px  ([base] x [multiplier]) — used for: [context]
  2xl:  [N]px  ([base] x [multiplier]) — used for: [context]

COMPONENT PADDING PATTERNS:
  Buttons:     [top] [right] [bottom] [left]
  Cards:       [top] [right] [bottom] [left]
  Inputs:      [top] [right] [bottom] [left]
  List items:  [top] [right] [bottom] [left]

GAP PATTERNS:
  Form fields:    [N]px between fields
  Button groups:  [N]px between buttons
  Section gap:    [N]px between major sections
```

## Phase 5: Component Cataloging

Identify and document every distinct UI component visible in the screenshot.

### Extraction Process

For each component:

1. **Name it** -- Use standard terminology (button, input, card, badge, avatar, tab, etc.).
2. **Count variants** -- How many visual variants are visible? (primary/secondary/ghost button, filled/outlined input).
3. **Identify states** -- Which states are visible? (default, hover, active, disabled, focused, selected, error).
4. **Measure it** -- Height, padding, border-radius, font size, icon size.
5. **Note composition** -- What sub-elements does it contain? (icon + label, avatar + name + subtitle).

### Output Format

For each component:

```
COMPONENT: [Name]
  Variants observed: [list]
  States visible: [list]
  States NOT visible: [list — mark as gap]
  Dimensions:
    Height: ~[N]px
    Padding: [values]
    Border radius: [N]px
    Font size: ~[N]px
    Font weight: [N]
    Icon size: [N]px (if applicable)
  Colors:
    Background: #XXXXXX
    Text: #XXXXXX
    Border: #XXXXXX (if applicable)
    Icon: #XXXXXX (if applicable)
  Composition: [sub-elements]
  Notes: [anything unusual or distinctive]
```

### Common Component Checklist

Scan for each of these. Mark present or absent:

- [ ] Button (primary, secondary, ghost, icon-only)
- [ ] Text input / search bar
- [ ] Dropdown / select
- [ ] Checkbox / toggle / radio
- [ ] Card / panel
- [ ] Navigation bar / header
- [ ] Sidebar / drawer
- [ ] Tab bar / segmented control
- [ ] List item / row
- [ ] Badge / tag / chip
- [ ] Avatar / icon
- [ ] Modal / dialog
- [ ] Toast / notification
- [ ] Tooltip / popover
- [ ] Divider / separator
- [ ] Loading / skeleton state
- [ ] Empty state

## Phase 6: Layout Structure

Document the spatial organization and visual hierarchy of the interface.

### Extraction Process

1. **Grid system** -- Identify columns, gutters, and margins. Note whether a standard grid (12-column) or custom layout is used.
2. **Content hierarchy** -- Rank content areas by visual prominence (size, position, contrast, whitespace).
3. **Section mapping** -- Divide the interface into named sections (header, sidebar, main content, footer, etc.).
4. **Visual weight** -- Note where the eye is drawn first, second, third. Identify what creates that hierarchy (size, color, contrast, position).
5. **Alignment axes** -- Identify the dominant alignment pattern (left-aligned, center-aligned, mixed).

### Output Format

```
GRID:
  Type: [fixed/fluid/hybrid]
  Columns: [N]
  Gutter: ~[N]px
  Margin: ~[N]px
  Max width: ~[N]px (if constrained)

SECTION MAP:
  [Section name]: [position, approximate dimensions, role]
  [Section name]: [position, approximate dimensions, role]
  ...

VISUAL HIERARCHY (reading order):
  1. [Element/area] — draws attention via [mechanism]
  2. [Element/area] — secondary focus via [mechanism]
  3. [Element/area] — tertiary via [mechanism]

ALIGNMENT:
  Primary axis: [left/center/mixed]
  Notable breaks: [any deliberate alignment breaks]

CONTENT DENSITY:
  [Section]: [sparse/moderate/dense]
```

## Phase 7: Border and Elevation

Document the depth strategy, border treatments, and shadow system.

### Extraction Process

1. **Border radii** -- Measure distinct radius values. Note which components use which radius.
2. **Border colors and widths** -- Document border treatments. Note opacity if semi-transparent.
3. **Shadow values** -- Identify distinct shadow levels. Estimate offset, blur, spread, and color.
4. **Elevation hierarchy** -- Map which elements sit above which. Number the levels.
5. **Divider patterns** -- How are sections separated? (borders, spacing, background shifts, shadows).
6. **Depth strategy** -- Classify the overall approach: borders-only, subtle shadows, layered shadows, or surface shifts.

### Output Format

```
DEPTH STRATEGY: [borders-only / subtle-shadows / layered-shadows / surface-shifts]

BORDER RADII:
  Small (buttons, inputs):  [N]px
  Medium (cards, panels):   [N]px
  Large (modals, sheets):   [N]px
  Full (avatars, pills):    [N]px (9999px / 50%)

SHADOWS:
  Level 1 (subtle):   [offset-x] [offset-y] [blur] [spread] [color]
  Level 2 (medium):   [offset-x] [offset-y] [blur] [spread] [color]
  Level 3 (elevated): [offset-x] [offset-y] [blur] [spread] [color]

BORDER TREATMENTS:
  Default: [width] [style] [color]
  Subtle:  [width] [style] [color]
  Strong:  [width] [style] [color]

ELEVATION MAP:
  Level 0: [elements at base level]
  Level 1: [elements floating above base]
  Level 2: [elements above level 1]
  Level 3: [highest elevation elements]

DIVIDER PATTERN: [description of how sections are separated]
```

## Phase 8: Output Assembly

Compile all phase outputs into a single structured extraction document.

### Assembly Process

1. **Compile all phases** -- Gather outputs from Phases 1-7 into a single document.
2. **Cross-reference** -- Verify color references in components match the color palette. Verify spacing values in components match the spacing scale.
3. **Resolve conflicts** -- If a component's measured padding does not match the spacing scale, note the discrepancy.
4. **Document gaps** -- Compile all acknowledged gaps into a single section.
5. **Add implementation notes** -- For each token category, add CSS custom property suggestions or Tailwind config hints.

### Gaps Section (Required)

Every extraction MUST end with an honest gaps section:

```
KNOWN GAPS:
  Cannot determine from static screenshot:
  - [ ] Hover states for [components]
  - [ ] Focus ring styles
  - [ ] Animation/transition properties
  - [ ] Responsive breakpoint behavior
  - [ ] Touch target sizes (if mobile)
  - [ ] Scroll behavior
  - [ ] [Other gaps specific to this screenshot]

  Low confidence extractions:
  - [ ] [Item] — reason for low confidence
  - [ ] [Item] — reason for low confidence
```

Never fabricate values for gaps. State what is unknown and suggest how to obtain the missing information (e.g., "inspect the live app," "request additional screenshots at different viewport widths").

### Implementation Hints (Optional)

When the user intends to implement the extracted system, include a CSS custom properties mapping or Tailwind configuration snippet. See [references/implementation-templates.md](references/implementation-templates.md) for starter templates.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Guessing hex values instead of acknowledging approximation | Prefix all color values with context; use `~` for uncertain sizes |
| Extracting colors without assigning roles | Every color must have a named role (primary, secondary, border, etc.) |
| Listing components without measuring them | Every component needs dimensions, padding, and radius values |
| Ignoring the spacing system | Identify the base unit first; express all spacing as multiples |
| Skipping the gaps section | Always document what cannot be determined from a static image |
| Treating all text sizes as a flat list | Organize into a hierarchical scale with named levels |
| Extracting shadows without noting the depth strategy | Classify the overall approach before listing individual shadow values |
| Providing vague font identification | State confidence level; suggest closest known match |

## Quality Checklist

Before delivering any screenshot analysis:

**Completeness:**
- [ ] All 8 phases addressed
- [ ] Initial assessment establishes platform and context
- [ ] Color palette organized by role with attributions
- [ ] Typography scale uses named hierarchy levels
- [ ] Spacing scale identifies base unit and multipliers
- [ ] Every visible component cataloged with measurements
- [ ] Layout structure includes grid, hierarchy, and alignment
- [ ] Border and elevation system documented

**Precision:**
- [ ] All colors include hex values
- [ ] All sizes include pixel estimates (with `~` where approximate)
- [ ] Font families include confidence level
- [ ] Component specs include dimensions, padding, radius, and colors
- [ ] Spacing values traceable to base unit

**Honesty:**
- [ ] Gaps section present and populated
- [ ] No fabricated hover/animation/responsive values
- [ ] Low-confidence extractions flagged
- [ ] Missing component states explicitly noted
