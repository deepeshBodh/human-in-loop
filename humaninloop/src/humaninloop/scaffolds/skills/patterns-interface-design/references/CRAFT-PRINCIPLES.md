# Core Craft Principles

These apply regardless of design direction. This is the quality floor.

## Table of Contents

1. [Surface and Token Architecture](#surface-and-token-architecture)
   - [The Primitive Foundation](#the-primitive-foundation)
   - [Surface Elevation Hierarchy](#surface-elevation-hierarchy)
   - [The Subtlety Principle](#the-subtlety-principle)
   - [Common AI Mistakes to Avoid](#common-ai-mistakes-to-avoid)
   - [Text Hierarchy via Tokens](#text-hierarchy-via-tokens)
   - [Border Progression](#border-progression)
   - [Dedicated Control Tokens](#dedicated-control-tokens)
   - [Context-Aware Bases](#context-aware-bases)
   - [Alternative Backgrounds for Depth](#alternative-backgrounds-for-depth)
2. [Spacing System](#spacing-system)
3. [Border Radius Consistency](#border-radius-consistency)
4. [Depth and Elevation Strategy](#depth-and-elevation-strategy)
5. [Card Layouts](#card-layouts)
6. [Isolated Controls](#isolated-controls)
7. [Typography Hierarchy](#typography-hierarchy)
8. [Monospace for Data](#monospace-for-data)
9. [Iconography](#iconography)
10. [Animation](#animation)
11. [Contrast Hierarchy](#contrast-hierarchy)
12. [Color Carries Meaning](#color-carries-meaning)
13. [Navigation Context](#navigation-context)
14. [Dark Mode Considerations](#dark-mode-considerations)

---

## Surface and Token Architecture

Professional interfaces build systems, not random choices. Understanding this architecture separates "looks okay" from "feels like a real product."

### The Primitive Foundation

Every color in the interface should trace back to a small set of primitives:

| Primitive | Purpose | Examples |
|-----------|---------|----------|
| **Foreground** | Text colors | primary, secondary, muted |
| **Background** | Surface colors | base, elevated, overlay |
| **Border** | Edge colors | default, subtle, strong |
| **Brand** | Primary accent | Single brand color |
| **Semantic** | Functional colors | destructive, warning, success |

Do not invent new colors. Map everything to these primitives.

### Surface Elevation Hierarchy

Surfaces stack. A dropdown sits above a card which sits above the page. Build a numbered system:

```
Level 0: Base background (the app canvas)
Level 1: Cards, panels (same visual plane as base)
Level 2: Dropdowns, popovers (floating above)
Level 3: Nested dropdowns, stacked overlays
Level 4: Highest elevation (rare)
```

In dark mode, higher elevation = slightly lighter. In light mode, higher elevation = slightly lighter or uses shadow. The principle: **elevated surfaces need visual distinction from what is beneath them.**

### The Subtlety Principle

This is where most interfaces fail. Study Vercel, Supabase, Linear. Their surfaces are **barely different** but still distinguishable. Their borders are **light but not invisible**.

**For surfaces:** The difference between elevation levels should be subtle. A few percentage points of lightness, not dramatic jumps. In dark mode:
- surface-100: 7% lighter than base
- surface-200: 9% lighter than base
- surface-300: 12% lighter than base

The difference is barely visible, but it is felt.

**For borders:** Borders should define regions without demanding attention. Use low opacity:
- Dark mode: 0.05-0.12 alpha
- Light mode: slightly higher

The border should disappear when not looking for it, but be findable when understanding structure is needed.

**The squint test:** Squint at the interface. Hierarchy should still be perceivable. What is above what, where regions begin and end. But no single border or surface should jump out. If borders are the first thing noticed, they are too strong. If region boundaries are unfindable, they are too subtle.

### Common AI Mistakes to Avoid

| Mistake | Problem | Fix |
|---------|---------|-----|
| Borders too visible | 1px solid gray demands attention | Use subtle rgba borders |
| Dramatic surface jumps | Dark to light instead of gradual | Subtle lightness progression |
| Different hues for surfaces | Gray card on blue background | Same hue family throughout |
| Harsh dividers | Strong hr elements | Subtle borders where needed |

### Text Hierarchy via Tokens

Build four levels, not just "text" and "gray text":

| Level | Purpose | Contrast |
|-------|---------|----------|
| **Primary** | Default text | Highest |
| **Secondary** | Supporting text | Slightly muted |
| **Tertiary** | Metadata, timestamps | Less important |
| **Muted** | Disabled, placeholder | Lowest |

Use all four consistently. If only two are in use, hierarchy is too flat.

### Border Progression

Borders are not binary. Build a scale:

| Level | Purpose |
|-------|---------|
| **Default** | Standard borders |
| **Subtle/Muted** | Softer separation |
| **Strong** | Emphasis, hover states |
| **Stronger** | Maximum emphasis, focus rings |

Match border intensity to boundary importance.

### Dedicated Control Tokens

Form controls (inputs, checkboxes, selects) have specific needs. Do not reuse surface tokens. Create dedicated ones:

| Token | Purpose |
|-------|---------|
| Control background | Often different from surface backgrounds |
| Control border | Needs to feel interactive |
| Control focus | Clear focus indication |

This separation allows tuning controls independently from layout surfaces.

### Context-Aware Bases

Different areas of the app might need different base surfaces:

| Area | Treatment |
|------|-----------|
| Marketing pages | Darker/richer backgrounds |
| Dashboard/app | Neutral working backgrounds |
| Sidebar | May differ from main canvas |

The surface hierarchy works the same way. It just starts from a different base.

### Alternative Backgrounds for Depth

Beyond shadows, use contrasting backgrounds to create depth. An "alternative" or "inset" background makes content feel recessed. Useful for:

- Empty states in data grids
- Code blocks
- Inset panels
- Visual grouping without borders

---

## Spacing System

Pick a base unit (4px and 8px are common) and use multiples throughout. The specific number matters less than consistency. Every spacing value should be explainable as "X times the base unit."

Build a scale for different contexts:

| Context | Purpose | Example (8px base) |
|---------|---------|-------------------|
| Micro | Icon gaps, tight element pairs | 4px, 8px |
| Component | Within buttons, inputs, cards | 8px, 12px, 16px |
| Section | Between related groups | 24px, 32px |
| Major | Between distinct sections | 48px, 64px |

### Symmetrical Padding Rule

TLBR must match. If top padding is 16px, left/bottom/right must also be 16px.

Exception: when content naturally creates visual balance.

```css
/* Correct */
padding: 16px;
padding: 12px 16px; /* Only when horizontal needs more room */

/* Avoid */
padding: 24px 16px 12px 16px;
```

---

## Border Radius Consistency

Sharper corners feel technical. Rounder corners feel friendly. Pick a scale that fits the product's personality and use it consistently.

| Element | Radius Scale |
|---------|--------------|
| Inputs, buttons | Small |
| Cards | Medium |
| Modals, containers | Large |

Do not mix sharp and soft randomly. Inconsistent radius is as jarring as inconsistent spacing.

---

## Depth and Elevation Strategy

Match the depth approach to the design direction. Choose ONE and commit:

### Borders-Only (Flat)

Clean, technical, dense. Works for utility-focused tools where information density matters more than visual lift. Linear, Raycast, and many developer tools use almost no shadows.

```css
--border: rgba(0, 0, 0, 0.08);
--border-subtle: rgba(0, 0, 0, 0.05);
border: 0.5px solid var(--border);
```

### Subtle Single Shadows

Soft lift without complexity. Works for approachable products that want gentle depth.

```css
--shadow: 0 1px 3px rgba(0,0,0,0.08);
```

### Layered Shadows

Rich, premium, dimensional. Multiple shadow layers create realistic depth. Stripe and Mercury use this approach. Best for cards that need to feel like physical objects.

```css
--shadow-layered:
  0 0 0 0.5px rgba(0, 0, 0, 0.05),
  0 1px 2px rgba(0, 0, 0, 0.04),
  0 2px 4px rgba(0, 0, 0, 0.03),
  0 4px 8px rgba(0, 0, 0, 0.02);
```

### Surface Color Shifts

Background tints establish hierarchy without any shadows. A card at #fff on a #f8fafc background already feels elevated.

---

## Card Layouts

Monotonous card layouts are lazy design. A metric card does not have to look like a plan card does not have to look like a settings card.

Design each card's internal structure for its specific content. But keep the surface treatment consistent:
- Same border weight
- Same shadow depth
- Same corner radius
- Same padding scale
- Same typography

---

## Isolated Controls

UI controls deserve container treatment. Date pickers, filters, dropdowns should feel like crafted objects.

**Never use native form elements for styled UI.** Native select, input type="date", and similar elements render OS-native dropdowns that cannot be styled.

Build custom components instead:
- Custom select: trigger button + positioned dropdown menu
- Custom date picker: input + calendar popover
- Custom checkbox/radio: styled div with state management

Custom select triggers must use `display: inline-flex` with `white-space: nowrap` to keep text and chevron icons on the same row.

---

## Typography Hierarchy

Build distinct levels that are visually distinguishable at a glance:

| Level | Treatment |
|-------|-----------|
| **Headlines** | Heavier weight, tighter letter-spacing for presence |
| **Body** | Comfortable weight for readability |
| **Labels/UI** | Medium weight, works at smaller sizes |
| **Data** | Often monospace, needs tabular-nums for alignment |

Do not rely on size alone. Combine size, weight, and letter-spacing to create clear hierarchy. If squinting makes headline and body indistinguishable, the hierarchy is too weak.

---

## Monospace for Data

Numbers, IDs, codes, timestamps belong in monospace. Use `tabular-nums` for columnar alignment. Mono signals "this is data."

---

## Iconography

Icons clarify, not decorate. If removing an icon loses no meaning, remove it. Choose a consistent icon set and stick with it throughout the product.

Give standalone icons presence with subtle background containers. Icons next to text should align optically, not mathematically.

---

## Animation

Keep it fast and functional.

| Interaction Type | Duration |
|------------------|----------|
| Micro-interactions (hover, focus) | ~150ms |
| Larger transitions (modals, panels) | 200-250ms |

Use smooth deceleration easing (ease-out variants). Avoid spring/bounce effects in professional interfaces. They feel playful, not serious.

---

## Contrast Hierarchy

Build a four-level system:
1. Foreground (primary)
2. Secondary
3. Muted
4. Faint

Use all four consistently.

---

## Color Carries Meaning

Gray builds structure. Color communicates:
- Status
- Action
- Emphasis
- Identity

Unmotivated color is noise. Color that reinforces the product's world is character.

---

## Navigation Context

Screens need grounding. A data table floating in space feels like a component demo, not a product. Consider including:

| Element | Purpose |
|---------|---------|
| Navigation | Sidebar or top nav showing location |
| Location indicator | Breadcrumbs, page title, active nav state |
| User context | Who is logged in, what workspace/org |

When building sidebars, consider using the same background as the main content area. Rely on a subtle border for separation rather than different background colors.

---

## Dark Mode Considerations

Dark interfaces have different needs:

| Aspect | Treatment |
|--------|-----------|
| **Borders over shadows** | Shadows are less visible on dark backgrounds. Lean more on borders for definition. |
| **Semantic colors** | Status colors (success, warning, error) often need slight desaturation for dark backgrounds. |
| **Same structure** | The hierarchy system still applies, just with inverted values. |
