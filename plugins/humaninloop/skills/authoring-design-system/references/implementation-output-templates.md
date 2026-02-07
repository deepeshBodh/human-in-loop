# Implementation Output Templates

Templates for translating a unified design system into platform-specific code. These extend the single-extraction templates from `humaninloop:analysis-screenshot` with multi-source attribution and conflict resolution comments.

## CSS Custom Properties

```css
:root {
  /* ========================================
   * Design System: [System Name]
   * Sources: [Source 1], [Source 2], [Source 3]
   * Generated: [Date]
   * ======================================== */

  /* === Colors: Brand === */
  /* from: [Source Name] */
  --color-brand-primary: #XXXXXX;
  --color-brand-secondary: #XXXXXX;

  /* === Colors: Neutral === */
  /* from: [Source Name] | conflict C-001 resolved */
  --color-bg-base: #XXXXXX;
  /* from: [Source Name] */
  --color-bg-elevated: #XXXXXX;
  --color-bg-surface: #XXXXXX;
  --color-bg-overlay: #XXXXXX;
  /* from: [Source Name] */
  --color-border-default: #XXXXXX;
  --color-border-subtle: #XXXXXX;
  --color-border-strong: #XXXXXX;
  /* from: [Source Name] */
  --color-text-primary: #XXXXXX;
  --color-text-secondary: #XXXXXX;
  --color-text-muted: #XXXXXX;
  --color-text-inverse: #XXXXXX;

  /* === Colors: Semantic === */
  --color-success: #XXXXXX;       /* from: [Source Name] */
  --color-success-subtle: #XXXXXX;
  --color-warning: #XXXXXX;       /* from: [Source Name] */
  --color-warning-subtle: #XXXXXX;
  --color-error: #XXXXXX;         /* from: [Source Name] */
  --color-error-subtle: #XXXXXX;
  --color-info: #XXXXXX;          /* from: [Source Name] */
  --color-info-subtle: #XXXXXX;

  /* === Colors: Accent === */
  --color-accent-1: #XXXXXX;      /* from: [Source Name] */
  --color-accent-2: #XXXXXX;      /* from: [Source Name] */

  /* === Typography === */
  /* from: [Source Name] */
  --font-family-primary: 'FontName', system-ui, sans-serif;
  --font-family-mono: 'MonoFont', ui-monospace, monospace;

  /* Type scale — from: [Source Name] | conflict C-NNN resolved */
  --font-size-display: Xrem;
  --font-size-h1: Xrem;
  --font-size-h2: Xrem;
  --font-size-h3: Xrem;
  --font-size-body: Xrem;
  --font-size-body-sm: Xrem;
  --font-size-caption: Xrem;
  --font-size-label: Xrem;
  --font-size-overline: Xrem;

  /* Weight scale */
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Leading */
  --leading-tight: 1.2;
  --leading-snug: 1.35;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* Tracking */
  --tracking-tight: -0.02em;
  --tracking-normal: 0;
  --tracking-wide: 0.05em;

  /* === Spacing === */
  /* Base unit from: [Source Name] | conflict C-NNN resolved */
  --space-base: Xpx;
  --space-3xs: calc(var(--space-base) * 0.125);  /* Xpx */
  --space-2xs: calc(var(--space-base) * 0.25);   /* Xpx */
  --space-xs: calc(var(--space-base) * 0.5);     /* Xpx */
  --space-sm: var(--space-base);                  /* Xpx */
  --space-md: calc(var(--space-base) * 1.5);     /* Xpx */
  --space-lg: calc(var(--space-base) * 2);       /* Xpx */
  --space-xl: calc(var(--space-base) * 3);       /* Xpx */
  --space-2xl: calc(var(--space-base) * 4);      /* Xpx */
  --space-3xl: calc(var(--space-base) * 6);      /* Xpx */
  --space-4xl: calc(var(--space-base) * 8);      /* Xpx */

  /* === Border Radius === */
  --radius-xs: Xpx;    /* from: [Source Name] */
  --radius-sm: Xpx;    /* from: [Source Name] */
  --radius-md: Xpx;    /* from: [Source Name] | conflict C-NNN */
  --radius-lg: Xpx;    /* from: [Source Name] */
  --radius-xl: Xpx;    /* from: [Source Name] */
  --radius-full: 9999px;

  /* === Shadows === */
  /* Depth strategy: [borders-only / subtle-shadows / layered-shadows / surface-shifts] */
  /* from: [Source Name] */
  --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.04);
  --shadow-sm: 0 2px 4px -1px rgb(0 0 0 / 0.06);
  --shadow-md: 0 4px 8px -2px rgb(0 0 0 / 0.08);
  --shadow-lg: 0 8px 16px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 16px 32px -8px rgb(0 0 0 / 0.12);

  /* === Borders === */
  --border-width-thin: 1px;
  --border-width-default: 1px;
  --border-width-thick: 2px;
  --border-default: var(--border-width-default) solid var(--color-border-default);
  --border-subtle: var(--border-width-thin) solid var(--color-border-subtle);
  --border-strong: var(--border-width-thick) solid var(--color-border-strong);

  /* === Z-Index Scale === */
  --z-base: 0;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-overlay: 300;
  --z-modal: 400;
  --z-toast: 500;
}
```

## Tailwind CSS Configuration

```js
// tailwind.config.js
// Design System: [System Name]
// Sources: [Source 1], [Source 2], [Source 3]

module.exports = {
  theme: {
    colors: {
      brand: {
        primary: '#XXXXXX',   // from: [Source Name]
        secondary: '#XXXXXX', // from: [Source Name]
      },
      bg: {
        base: '#XXXXXX',      // from: [Source Name] | conflict C-001
        elevated: '#XXXXXX',  // from: [Source Name]
        surface: '#XXXXXX',   // from: [Source Name]
        overlay: '#XXXXXX',   // from: [Source Name]
      },
      text: {
        primary: '#XXXXXX',
        secondary: '#XXXXXX',
        muted: '#XXXXXX',
        inverse: '#XXXXXX',
      },
      border: {
        DEFAULT: '#XXXXXX',
        subtle: '#XXXXXX',
        strong: '#XXXXXX',
      },
      success: { DEFAULT: '#XXXXXX', subtle: '#XXXXXX' },
      warning: { DEFAULT: '#XXXXXX', subtle: '#XXXXXX' },
      error: { DEFAULT: '#XXXXXX', subtle: '#XXXXXX' },
      info: { DEFAULT: '#XXXXXX', subtle: '#XXXXXX' },
      accent: {
        1: '#XXXXXX',
        2: '#XXXXXX',
      },
    },
    fontFamily: {
      sans: ['FontName', 'system-ui', 'sans-serif'],   // from: [Source Name]
      mono: ['MonoFont', 'ui-monospace', 'monospace'],  // from: [Source Name]
    },
    fontSize: {
      display: ['Xrem', { lineHeight: '1.2', fontWeight: '700', letterSpacing: '-0.02em' }],
      h1: ['Xrem', { lineHeight: '1.2', fontWeight: '700', letterSpacing: '-0.02em' }],
      h2: ['Xrem', { lineHeight: '1.3', fontWeight: '600' }],
      h3: ['Xrem', { lineHeight: '1.3', fontWeight: '600' }],
      body: ['Xrem', { lineHeight: '1.5', fontWeight: '400' }],
      'body-sm': ['Xrem', { lineHeight: '1.5', fontWeight: '400' }],
      caption: ['Xrem', { lineHeight: '1.5', fontWeight: '400' }],
      label: ['Xrem', { lineHeight: '1.5', fontWeight: '500' }],
      overline: ['Xrem', { lineHeight: '1.5', fontWeight: '600', letterSpacing: '0.05em' }],
    },
    spacing: {
      '3xs': 'Xpx',
      '2xs': 'Xpx',
      xs: 'Xpx',
      sm: 'Xpx',
      md: 'Xpx',
      lg: 'Xpx',
      xl: 'Xpx',
      '2xl': 'Xpx',
      '3xl': 'Xpx',
      '4xl': 'Xpx',
    },
    borderRadius: {
      xs: 'Xpx',
      sm: 'Xpx',
      md: 'Xpx',
      lg: 'Xpx',
      xl: 'Xpx',
      full: '9999px',
    },
    boxShadow: {
      xs: '0 1px 2px 0 rgb(0 0 0 / 0.04)',
      sm: '0 2px 4px -1px rgb(0 0 0 / 0.06)',
      md: '0 4px 8px -2px rgb(0 0 0 / 0.08)',
      lg: '0 8px 16px -4px rgb(0 0 0 / 0.1)',
      xl: '0 16px 32px -8px rgb(0 0 0 / 0.12)',
    },
    zIndex: {
      base: '0',
      dropdown: '100',
      sticky: '200',
      overlay: '300',
      modal: '400',
      toast: '500',
    },
  },
}
```

## SwiftUI Token Mapping

```swift
// DesignTokens.swift
// Design System: [System Name]
// Sources: [Source 1], [Source 2], [Source 3]
import SwiftUI

enum DesignTokens {

    // MARK: - Colors

    enum Colors {
        // Brand — from: [Source Name]
        static let brandPrimary = Color(hex: "#XXXXXX")
        static let brandSecondary = Color(hex: "#XXXXXX")

        // Backgrounds — from: [Source Name] | conflict C-001
        static let bgBase = Color(hex: "#XXXXXX")
        static let bgElevated = Color(hex: "#XXXXXX")
        static let bgSurface = Color(hex: "#XXXXXX")
        static let bgOverlay = Color(hex: "#XXXXXX")

        // Text
        static let textPrimary = Color(hex: "#XXXXXX")
        static let textSecondary = Color(hex: "#XXXXXX")
        static let textMuted = Color(hex: "#XXXXXX")
        static let textInverse = Color(hex: "#XXXXXX")

        // Borders
        static let borderDefault = Color(hex: "#XXXXXX")
        static let borderSubtle = Color(hex: "#XXXXXX")
        static let borderStrong = Color(hex: "#XXXXXX")

        // Semantic
        static let success = Color(hex: "#XXXXXX")
        static let warning = Color(hex: "#XXXXXX")
        static let error = Color(hex: "#XXXXXX")
        static let info = Color(hex: "#XXXXXX")
    }

    // MARK: - Typography

    enum Typography {
        // from: [Source Name]
        static let display = Font.system(size: X, weight: .bold)
        static let heading1 = Font.system(size: X, weight: .bold)
        static let heading2 = Font.system(size: X, weight: .semibold)
        static let heading3 = Font.system(size: X, weight: .semibold)
        static let body = Font.system(size: X, weight: .regular)
        static let bodySmall = Font.system(size: X, weight: .regular)
        static let caption = Font.system(size: X, weight: .regular)
        static let label = Font.system(size: X, weight: .medium)
        static let overline = Font.system(size: X, weight: .semibold)
    }

    // MARK: - Spacing

    enum Spacing {
        // Base unit from: [Source Name] | conflict C-NNN
        static let base: CGFloat = X
        static let xxxs: CGFloat = base * 0.125
        static let xxs: CGFloat = base * 0.25
        static let xs: CGFloat = base * 0.5
        static let sm: CGFloat = base
        static let md: CGFloat = base * 1.5
        static let lg: CGFloat = base * 2
        static let xl: CGFloat = base * 3
        static let xxl: CGFloat = base * 4
        static let xxxl: CGFloat = base * 6
    }

    // MARK: - Radius

    enum Radius {
        static let xs: CGFloat = X
        static let sm: CGFloat = X
        static let md: CGFloat = X
        static let lg: CGFloat = X
        static let xl: CGFloat = X
    }

    // MARK: - Shadows

    enum Shadows {
        static let sm = ShadowStyle(color: .black.opacity(0.06), radius: 2, x: 0, y: 1)
        static let md = ShadowStyle(color: .black.opacity(0.08), radius: 4, x: 0, y: 2)
        static let lg = ShadowStyle(color: .black.opacity(0.1), radius: 8, x: 0, y: 4)
    }
}

struct ShadowStyle {
    let color: Color
    let radius: CGFloat
    let x: CGFloat
    let y: CGFloat
}

// MARK: - Color Hex Extension

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 6: (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default: (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
```

## Jetpack Compose Token Mapping

```kotlin
// DesignTokens.kt
// Design System: [System Name]
// Sources: [Source 1], [Source 2], [Source 3]

object DesignTokens {

    // Colors — Brand
    val brandPrimary = Color(0xFFXXXXXX)   // from: [Source Name]
    val brandSecondary = Color(0xFFXXXXXX) // from: [Source Name]

    // Colors — Background
    val bgBase = Color(0xFFXXXXXX)         // from: [Source Name] | conflict C-001
    val bgElevated = Color(0xFFXXXXXX)
    val bgSurface = Color(0xFFXXXXXX)

    // Colors — Text
    val textPrimary = Color(0xFFXXXXXX)
    val textSecondary = Color(0xFFXXXXXX)
    val textMuted = Color(0xFFXXXXXX)

    // Colors — Semantic
    val success = Color(0xFFXXXXXX)
    val warning = Color(0xFFXXXXXX)
    val error = Color(0xFFXXXXXX)
    val info = Color(0xFFXXXXXX)

    // Spacing
    val spaceBase = X.dp         // from: [Source Name]
    val space2xs = (spaceBase.value * 0.25f).dp
    val spaceXs = (spaceBase.value * 0.5f).dp
    val spaceSm = spaceBase
    val spaceMd = (spaceBase.value * 1.5f).dp
    val spaceLg = (spaceBase.value * 2f).dp
    val spaceXl = (spaceBase.value * 3f).dp
    val space2xl = (spaceBase.value * 4f).dp

    // Radius
    val radiusSm = X.dp
    val radiusMd = X.dp
    val radiusLg = X.dp
    val radiusFull = 9999.dp
}
```

## Usage Notes

- Replace all `#XXXXXX` and `0xFFXXXXXX` placeholders with values from the unified color palette
- Replace all `Xpx`, `Xrem`, and `X` placeholders with values from the consolidated type and spacing scales
- Replace `FontName` and `MonoFont` with the selected unified font families
- Replace `[Source Name]` comments with the actual extraction source names
- Replace `C-NNN` references with actual conflict IDs from the conflict resolution log
- Remove any token lines for values not present in the assembled system -- gaps remain explicit
- Add or remove scale levels based on what the unified system actually contains
- Shadow values should match the assembled elevation system, not these defaults
