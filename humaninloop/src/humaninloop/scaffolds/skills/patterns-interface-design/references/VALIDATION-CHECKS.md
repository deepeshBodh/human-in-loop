# Interface Design Validation Checks

Four validation checks ensure craft quality. Run these before finalizing any interface.

---

## 1. Spacing Validation

All spacing values must be multiples of the defined base unit.

### Check Process

1. Identify the base unit (4px, 8px, etc.)
2. Extract all spacing values from CSS/styles
3. Verify each is a multiple of base

### Valid Examples (8px base)

| Value | Multiple | Valid |
|-------|----------|-------|
| 8px | 1x | Yes |
| 16px | 2x | Yes |
| 24px | 3x | Yes |
| 32px | 4x | Yes |
| 12px | 1.5x | Acceptable for component internal |
| 14px | 1.75x | Violation |

### Common Violations

- Arbitrary padding values (17px, 23px, 41px)
- Mixed unit systems (some 8px based, some 10px based)
- Component-specific magic numbers

---

## 2. Depth Consistency Validation

The chosen depth strategy must apply consistently. Mixing strategies creates visual confusion.

### Check Process

1. Identify chosen strategy: borders-only, subtle shadows, layered shadows, or surface shifts
2. Scan all elevation points (cards, dropdowns, modals)
3. Verify same strategy throughout

### Strategy Detection

| If present | Strategy |
|------------|----------|
| No box-shadow, subtle borders only | Borders-only |
| Single soft shadow (0 1px 3px) | Subtle shadows |
| Multiple shadow layers | Layered shadows |
| Background color shifts, no shadows | Surface shifts |

### Common Violations

| Pattern | Problem |
|---------|---------|
| Cards with shadows + borders-only dropdowns | Mixed strategy |
| Some cards have shadows, others do not | Inconsistent |
| Layered shadows on cards, flat modals | Strategy mismatch |

### Borders-Only Means No Shadows

If borders-only strategy is chosen, verify:
- [ ] No box-shadow properties on containers
- [ ] No elevation classes that add shadows
- [ ] All depth comes from borders and background tints

---

## 3. Color Palette Validation

All colors must trace back to defined palette primitives. No arbitrary hex values.

### Check Process

1. Extract all color values from CSS/styles
2. Map each to a palette primitive (foreground, background, border, brand, semantic)
3. Flag any orphan colors

### Valid Color Sources

| Source | Examples |
|--------|----------|
| Foreground tokens | --text-primary, --text-secondary, --text-muted |
| Background tokens | --bg-base, --bg-elevated, --bg-overlay |
| Border tokens | --border-default, --border-subtle, --border-strong |
| Brand token | --brand-primary |
| Semantic tokens | --color-destructive, --color-warning, --color-success |

### Common Violations

| Pattern | Problem |
|---------|---------|
| Hardcoded #333333 for text | Should use foreground token |
| Random blue #2563eb inline | Should derive from brand or semantic |
| Different grays across components | Should use consistent background tokens |

### The Orphan Color Test

For each color value found:
1. Can it be named with a token? (text-secondary, border-subtle)
2. If not, is it derived from a primitive? (brand-primary with opacity)
3. If neither, it is an orphan. Remove or systematize it.

---

## 4. Pattern Reuse Validation

Documented patterns should be reused, not duplicated with variations.

### Check Process

1. Identify all component instances (buttons, cards, inputs)
2. Compare implementations
3. Flag structural differences that should be consistent

### Pattern Categories

| Category | What to check |
|----------|---------------|
| Buttons | Same padding, radius, transition timing |
| Cards | Same border treatment, shadow, padding scale |
| Inputs | Same height, border style, focus ring |
| Typography | Same font stacks, size scale, weight usage |

### Common Violations

| Pattern | Problem |
|---------|---------|
| Button A: 12px padding, Button B: 14px padding | Inconsistent |
| Card variant with different corner radius | Should use same radius |
| Input focus ring differs from button focus ring | Focus pattern should be global |

### The Copy-Paste Test

If a component looks like it was copied and modified slightly:
1. Identify what differs
2. Determine if difference is intentional (variant) or accidental (duplication)
3. Consolidate unintentional differences

---

## Validation Summary Checklist

Run before finalizing any interface:

### Spacing
- [ ] Base unit defined
- [ ] All values are multiples of base
- [ ] No magic numbers

### Depth
- [ ] Single strategy chosen
- [ ] Strategy applied to all elevation points
- [ ] No strategy mixing

### Colors
- [ ] Palette primitives defined
- [ ] All colors trace to primitives
- [ ] No orphan colors

### Patterns
- [ ] Component patterns documented
- [ ] Patterns reused consistently
- [ ] No unintentional duplication

---

## Quick Validation Commands

### CSS Variable Audit

Extract all CSS variables and categorize:

```bash
grep -r "var(--" . | cut -d'(' -f2 | cut -d')' -f1 | sort | uniq -c | sort -rn
```

### Hardcoded Color Audit

Find potential orphan colors:

```bash
grep -rE "#[0-9a-fA-F]{3,8}|rgb\(|rgba\(" . --include="*.css" --include="*.tsx" --include="*.jsx"
```

### Spacing Value Audit

Extract numeric pixel values:

```bash
grep -rE "[0-9]+px" . --include="*.css" --include="*.tsx" | grep -oE "[0-9]+px" | sort | uniq -c | sort -rn
```
