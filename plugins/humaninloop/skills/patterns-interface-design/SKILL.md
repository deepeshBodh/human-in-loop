---
name: patterns-interface-design
description: Use when designing UI components, pages, or applications, or when user mentions "interface design", "UI", "component design", "visual design", "styling", "dark mode", "spacing", "typography hierarchy", "surface elevation", or needs distinctive frontend aesthetics.
---

# Interface Design Patterns

## Core Mandate

**"The moment you stop asking 'why this?' is the moment defaults take over."**

Craft emerges from intentional choices, not pattern-following. Generic output happens when designers treat structural decisions (typography, navigation, data visualization) as mere infrastructure rather than design itself.

**Violating the letter of these rules is violating the spirit of these rules.** Following "most" of the discovery process or applying "some" intentional choices is not compliance.

## When to Use

- Building web components, pages, or applications
- Creating visual design systems
- Establishing typography, color, and spacing decisions
- Designing dark mode or light mode interfaces
- Crafting data visualization or dashboard layouts
- Making navigation or layout architecture decisions

## When NOT to Use

- Purely backend or API work
- Documentation-only tasks
- When design system already exists and must be followed exactly
- Quick prototypes where user explicitly wants minimal styling

## Required Discovery Process

Before proposing any direction, explore these four elements. Do not skip any.

### 1. Domain Exploration

Identify 5+ concepts native to the product's world. These are nouns, verbs, textures, and metaphors that belong to the domain. **Required even for familiar domains.**

| Product Type | Domain Concepts |
|--------------|-----------------|
| Financial dashboard | Ledger, balance, flow, precision, trust |
| Developer tools | Terminal, pipeline, build, deploy, logs |
| Healthcare | Vitals, chart, monitor, care, clinical |
| Creative tools | Canvas, brush, layer, blend, palette |

### 2. Color World

Identify 5+ colors that exist naturally in the product's physical or conceptual space. Build palettes that feel native, not applied over the product. **Required even when brand colors exist.**

| Product Type | Color World |
|--------------|-------------|
| Financial | Deep navy, muted gold, slate gray, paper white |
| Developer | Terminal green, dark gray, syntax highlighting hues |
| Healthcare | Clinical white, vital blue, alert amber, soft green |
| Creative | Rich pigments, canvas cream, ink black |

### 3. Signature Element

Define one distinctive element that could only belong to this product. This is the unforgettable detail. **Required even for internal tools.**

Examples:
- A specific border treatment unique to the brand
- An unconventional navigation pattern
- A distinctive loading animation
- A characteristic use of typography weight

### 4. Default Replacement

Name 3 obvious choices and deliberately replace them. If the first thing that comes to mind is the solution, it is probably a default. **Required even when defaults seem appropriate.**

| Default | Replacement Strategy |
|---------|---------------------|
| White cards on white background | Surface elevation via subtle tint |
| Standard 12-column grid | Asymmetric or breaking layout |
| Inter/Roboto font | Domain-appropriate typeface |
| Purple gradient accent | Color from product's world |

**No exceptions:**
- Not for "simple components"
- Not for "internal tools"
- Not for "MVP/prototype"
- Not even if user says "just make it look nice"

## Intent Specification

Define these three elements with specifics before coding:

1. **Who** — Identify the actual person using the interface
2. **What** — Define what they must accomplish (the verb)
3. **How** — Articulate how the interface should feel (beyond "clean" or "modern")

Intent must be systemic. Every token, color, and spacing decision reinforces the stated feeling.

## Surface and Token Architecture

Build systems, not random choices. See [CRAFT-PRINCIPLES.md](references/CRAFT-PRINCIPLES.md) for complete token architecture.

### Primitive Foundation

Every color traces back to these primitives:

| Primitive | Purpose |
|-----------|---------|
| Foreground | Text colors (primary, secondary, muted) |
| Background | Surface colors (base, elevated, overlay) |
| Border | Edge colors (default, subtle, strong) |
| Brand | Primary accent |
| Semantic | Functional colors (destructive, warning, success) |

### Surface Elevation

Surfaces stack. Build a numbered system:

```
Level 0: Base background (app canvas)
Level 1: Cards, panels (same visual plane)
Level 2: Dropdowns, popovers (floating above)
Level 3: Nested overlays (stacked)
Level 4: Highest elevation (rare)
```

In dark mode, higher elevation = slightly lighter. The difference between levels should be subtle: a few percentage points of lightness, not dramatic jumps.

### The Subtlety Principle

Study Vercel, Supabase, Linear. Their surfaces are barely different but still distinguishable. Their borders are light but not invisible.

**The squint test:** Squint at the interface. Hierarchy should remain perceivable. No single border or surface should jump out. If borders are the first thing noticed, they are too strong.

## Spacing System

Pick a base unit (4px or 8px). Use multiples throughout. Every spacing value should be explainable as "X times the base unit."

| Context | Spacing Scale |
|---------|---------------|
| Micro | Icon gaps, tight element pairs |
| Component | Within buttons, inputs, cards |
| Section | Between related groups |
| Major | Between distinct sections |

**Symmetrical padding rule:** TLBR must match. Exception: when content naturally creates visual balance.

```css
/* Correct */
padding: 16px;
padding: 12px 16px; /* Only when horizontal needs room */

/* Avoid */
padding: 24px 16px 12px 16px;
```

## Typography Hierarchy

Build distinct levels distinguishable at a glance:

| Level | Treatment |
|-------|-----------|
| Headlines | Heavier weight, tighter letter-spacing |
| Body | Comfortable weight for readability |
| Labels/UI | Medium weight, works at smaller sizes |
| Data | Often monospace, use tabular-nums |

Do not rely on size alone. Combine size, weight, and letter-spacing.

## Depth Strategy

Choose ONE approach and commit:

| Strategy | Character | When to Use |
|----------|-----------|-------------|
| Borders-only | Clean, technical, dense | Utility-focused tools |
| Subtle shadows | Soft lift, approachable | General applications |
| Layered shadows | Rich, premium, dimensional | Cards as physical objects |
| Surface shifts | Background tints establish hierarchy | Minimal, elegant |

Do not mix approaches. Inconsistent depth strategy is jarring.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Borders too visible | Use low opacity rgba (0.05-0.12 alpha for dark mode) |
| Dramatic surface jumps | Subtle lightness changes (2-5%) |
| Mixed hues for surfaces | Gray variations, same hue family |
| Harsh dividers | Subtle borders instead of hr elements |
| Missing interaction states | Define hover, focus, active for all controls |
| Pure white cards on color | Use tinted whites matching background |
| Decorative gradients | Gradients must serve function |

## Red Flags - STOP and Restart Properly

When any of these thoughts occur, STOP immediately:

- "This is just a simple component, defaults are fine"
- "The user wants it fast, skip discovery"
- "I already know what looks good here"
- "Inter/Roboto will work, no need to explore fonts"
- "Standard cards and shadows are professional enough"
- "This is internal tooling, aesthetics matter less"
- "Just make it clean and modern"

**All of these mean:** The discovery process is being skipped. Restart with proper exploration.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Requirements are clear, no discovery needed" | Discovery prevents template output. Do it anyway. |
| "User wants speed over exploration" | Exploration takes 5 minutes. Rework from generic output takes hours. |
| "This is a standard component" | Standard is exactly what discovery prevents. |
| "I know what works for this type of product" | Experience creates blind spots. Fresh exploration reveals better options. |
| "Defaults exist because they work" | Defaults exist because they are easy. Easy is not distinctive. |
| "Can refine aesthetics later" | "Later" rarely comes. Aesthetic debt compounds. Build right from start. |
| "Internal tool, users do not care" | Internal users deserve craft. Poor tools reduce productivity. |

## Quality Checklist

Before finalizing any interface design:

**Discovery:**
- [ ] 5+ domain concepts identified
- [ ] 5+ native colors explored
- [ ] Signature element defined
- [ ] 3 defaults named and replaced

**Intent:**
- [ ] User persona specified
- [ ] Core action (verb) defined
- [ ] Feeling articulated (not "clean" or "modern")

**Execution:**
- [ ] Token primitives established
- [ ] Surface elevation system defined
- [ ] Single depth strategy applied consistently
- [ ] Spacing uses base unit multiples
- [ ] Typography hierarchy distinguishable at squint test

**Validation:**
- [ ] Squint test passes (hierarchy visible, no element jumps out)
- [ ] No defaults remain unquestioned
- [ ] Signature element is memorable
