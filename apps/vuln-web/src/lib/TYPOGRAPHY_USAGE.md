# Chimera Typography System

This project uses the Recursive variable font with a complete typography system based on the Apparatus Design System.

## Font Import

The Recursive font is loaded from Google Fonts in `index.html` with full axis range:
- `wght` 300–900: Weight
- `MONO` 0–1: Monospace amount
- `CASL` 0–1: Casual warmth
- `slnt` -15–0: Slant/italic

## Using Typography Classes

### CSS Classes
Use the `.type-*` classes directly in your JSX:

```jsx
<h1 className="type-heading">Section Title</h1>
<p className="type-body">This is body text with warmth and readability.</p>
<span className="type-label">SIDEBAR LABEL</span>
<code className="type-code">const x = 42;</code>
```

### Available Classes
- `.type-display` — Page titles (36px, weight 300)
- `.type-heading` — Section headers (24px, weight 500)
- `.type-subhead` — Card subtitles (14px, weight 600)
- `.type-body` — Body text (13px, weight 400)
- `.type-label` — Sidebar labels (12px, weight 600, mono)
- `.type-tag` — Status badges (11px, weight 800)
- `.type-metric` — Big numbers (32px, weight 400, mono)
- `.type-metric-unit` — Units (13px, weight 500, mono)
- `.type-data` — Table cells (13px, weight 500, mono)
- `.type-code` — Code blocks (13px, weight 400, mono)
- `.type-timestamp` — Log times (11px, weight 500, mono)
- `.type-nav` — Navigation links (14px, half-mono)
- `.type-nav-active` — Active nav (14px, weight 700, half-mono)
- `.type-link` — Action links (10px, weight 700, italic)
- `.type-breadcrumb` — Breadcrumbs (10px, weight 700, mono italic)

### Using the Hook
For dynamic typography, use the `useTypography` hook:

```jsx
import { useTypography } from '../hooks/useTypography';

function MyComponent() {
  const heading = useTypography('heading');
  return <div style={heading.style} className={heading.className}>Title</div>;
}
```

### Direct Type System Import
For full control, import the type system directly:

```jsx
import { type, colors } from '../lib/type-system';

<div style={{
  fontVariationSettings: type.label.fontVariationSettings,
  fontSize: `${type.label.fontSize}px`,
  letterSpacing: type.label.letterSpacing,
  color: colors.textMuted,
}}>
  Label Text
</div>
```

## Brand Logic

- **CASL axis** encodes brand warmth: human-facing text (0.6), machine output (0)
- **MONO axis** separates prose from data: proportional for reading, monospace for precision
- **slnt axis** adds energy to navigation without weight changes

## Color Palette

Colors from the type-system module:
- `text`: #dce4ec (primary text)
- `textMuted`: #6d85a0 (secondary text)
- `textDim`: #4e6580 (decorative only)
- `magenta`: #d946a8 (Chimera accent)
- `blue`: #38a0ff (accent)
- `green`: #18c760 (success)
- `red`: #ef4444 (error)
