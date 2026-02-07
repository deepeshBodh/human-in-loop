# Implementation Templates

Starter templates for translating extracted design tokens into implementation-ready code. Use these as the foundation when assembling Phase 8 output.

## CSS Custom Properties

```css
:root {
  /* === Colors === */
  /* Brand */
  --color-brand-primary: #XXXXXX;
  --color-brand-secondary: #XXXXXX;

  /* Neutral */
  --color-bg-base: #XXXXXX;
  --color-bg-elevated: #XXXXXX;
  --color-bg-surface: #XXXXXX;
  --color-border-default: #XXXXXX;
  --color-border-subtle: #XXXXXX;
  --color-text-primary: #XXXXXX;
  --color-text-secondary: #XXXXXX;
  --color-text-muted: #XXXXXX;

  /* Semantic */
  --color-success: #XXXXXX;
  --color-warning: #XXXXXX;
  --color-error: #XXXXXX;
  --color-info: #XXXXXX;

  /* === Typography === */
  --font-family-primary: 'FontName', system-ui, sans-serif;
  --font-family-mono: 'MonoFont', ui-monospace, monospace;

  --font-size-display: Xrem;
  --font-size-h1: Xrem;
  --font-size-h2: Xrem;
  --font-size-h3: Xrem;
  --font-size-body: Xrem;
  --font-size-caption: Xrem;
  --font-size-label: Xrem;

  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --leading-tight: 1.2;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* === Spacing === */
  --space-base: Xpx;
  --space-2xs: calc(var(--space-base) * 0.25);
  --space-xs: calc(var(--space-base) * 0.5);
  --space-sm: calc(var(--space-base) * 1);
  --space-md: calc(var(--space-base) * 1.5);
  --space-lg: calc(var(--space-base) * 2);
  --space-xl: calc(var(--space-base) * 3);
  --space-2xl: calc(var(--space-base) * 4);
  --space-3xl: calc(var(--space-base) * 6);

  /* === Border Radius === */
  --radius-sm: Xpx;
  --radius-md: Xpx;
  --radius-lg: Xpx;
  --radius-full: 9999px;

  /* === Shadows === */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);

  /* === Borders === */
  --border-default: 1px solid var(--color-border-default);
  --border-subtle: 1px solid var(--color-border-subtle);
}
```

## Tailwind CSS Configuration

```js
// tailwind.config.js
module.exports = {
  theme: {
    colors: {
      brand: {
        primary: '#XXXXXX',
        secondary: '#XXXXXX',
      },
      bg: {
        base: '#XXXXXX',
        elevated: '#XXXXXX',
        surface: '#XXXXXX',
      },
      text: {
        primary: '#XXXXXX',
        secondary: '#XXXXXX',
        muted: '#XXXXXX',
      },
      border: {
        DEFAULT: '#XXXXXX',
        subtle: '#XXXXXX',
      },
      success: '#XXXXXX',
      warning: '#XXXXXX',
      error: '#XXXXXX',
      info: '#XXXXXX',
    },
    fontFamily: {
      sans: ['FontName', 'system-ui', 'sans-serif'],
      mono: ['MonoFont', 'ui-monospace', 'monospace'],
    },
    fontSize: {
      display: ['Xrem', { lineHeight: '1.2', fontWeight: '700' }],
      h1: ['Xrem', { lineHeight: '1.2', fontWeight: '700' }],
      h2: ['Xrem', { lineHeight: '1.3', fontWeight: '600' }],
      h3: ['Xrem', { lineHeight: '1.3', fontWeight: '600' }],
      body: ['Xrem', { lineHeight: '1.5', fontWeight: '400' }],
      caption: ['Xrem', { lineHeight: '1.5', fontWeight: '400' }],
      label: ['Xrem', { lineHeight: '1.5', fontWeight: '500' }],
    },
    spacing: {
      '2xs': 'Xpx',
      xs: 'Xpx',
      sm: 'Xpx',
      md: 'Xpx',
      lg: 'Xpx',
      xl: 'Xpx',
      '2xl': 'Xpx',
      '3xl': 'Xpx',
    },
    borderRadius: {
      sm: 'Xpx',
      md: 'Xpx',
      lg: 'Xpx',
      full: '9999px',
    },
    boxShadow: {
      sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
      md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
      lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
    },
  },
}
```

## SwiftUI Token Mapping

```swift
// DesignTokens.swift
import SwiftUI

enum DesignTokens {
    // MARK: - Colors
    enum Colors {
        static let brandPrimary = Color(hex: "#XXXXXX")
        static let brandSecondary = Color(hex: "#XXXXXX")
        static let bgBase = Color(hex: "#XXXXXX")
        static let bgElevated = Color(hex: "#XXXXXX")
        static let textPrimary = Color(hex: "#XXXXXX")
        static let textSecondary = Color(hex: "#XXXXXX")
        static let textMuted = Color(hex: "#XXXXXX")
    }

    // MARK: - Typography
    enum Typography {
        static let display = Font.system(size: X, weight: .bold)
        static let heading1 = Font.system(size: X, weight: .bold)
        static let heading2 = Font.system(size: X, weight: .semibold)
        static let body = Font.system(size: X, weight: .regular)
        static let caption = Font.system(size: X, weight: .regular)
    }

    // MARK: - Spacing
    enum Spacing {
        static let xxs: CGFloat = X
        static let xs: CGFloat = X
        static let sm: CGFloat = X
        static let md: CGFloat = X
        static let lg: CGFloat = X
        static let xl: CGFloat = X
    }

    // MARK: - Radius
    enum Radius {
        static let sm: CGFloat = X
        static let md: CGFloat = X
        static let lg: CGFloat = X
    }
}
```

## Usage Notes

- Replace all `#XXXXXX` placeholders with extracted hex values from Phase 2
- Replace all `Xpx` and `Xrem` placeholders with extracted values from Phases 3-4
- Replace `FontName` and `MonoFont` with identified font families from Phase 3
- Adjust shadow values to match extracted values from Phase 7
- Add or remove token levels based on what was actually observed in the screenshot
- Do not include tokens for values that were not extracted -- leave gaps explicit
