/**
 * Apparatus Design System — Typography
 * Font: Recursive (variable)
 * https://www.recursive.design
 *
 * Axes:
 *   wght  300–900   Weight
 *   MONO  0–1       Monospace (0 = proportional sans, 1 = monospace)
 *   CASL  0–1       Casual (0 = linear/sharp, 1 = soft/hand-drawn)
 *   CRSV  0–1       Cursive (auto italic behavior, keep at 0.5)
 *   slnt  -15–0     Slant (0 = upright, -15 = full italic)
 *
 * Brand logic:
 *   CASL encodes warmth — human-facing text is casual, machine output is clinical.
 *   MONO separates prose from data — proportional for reading, mono for precision.
 *   slnt adds lean/energy to navigational elements without changing weight.
 */

export const fontFamily = "'Recursive', ui-monospace, monospace";

// Google Fonts import (full axis range)
export const fontImport =
  "https://fonts.googleapis.com/css2?family=Recursive:slnt,wght,CASL,CRSV,MONO@-15..0,300..900,0..1,0..1,0..1&display=swap";

// ─── ROLE DEFINITIONS ──────────────────────────────────────

export const type = {
  /** Page titles, hero text — light weight, no personality */
  display: {
    fontVariationSettings: "'wght' 300, 'MONO' 0, 'CASL' 0, 'CRSV' 0.5, 'slnt' 0",
    fontSize: 36,
  },

  /** Section headers, card titles — slight casual warmth */
  heading: {
    fontVariationSettings: "'wght' 500, 'MONO' 0, 'CASL' 0.2, 'CRSV' 0.5, 'slnt' 0",
    fontSize: 24,
  },

  /** Card subtitles, secondary headers — subtle lean */
  subhead: {
    fontVariationSettings: "'wght' 600, 'MONO' 0, 'CASL' 0.3, 'CRSV' 0.5, 'slnt' -3",
    fontSize: 14,
    letterSpacing: "1.5px",
  },

  /** Descriptions, tooltips, longer text — warmest casual for readability */
  body: {
    fontVariationSettings: "'wght' 400, 'MONO' 0, 'CASL' 0.6, 'CRSV' 0.5, 'slnt' 0",
    fontSize: 13,
  },

  /** Sidebar group headers, section tags — mono with lean */
  label: {
    fontVariationSettings: "'wght' 600, 'MONO' 1, 'CASL' 0.3, 'CRSV' 0.5, 'slnt' -4",
    fontSize: 12,
    letterSpacing: "1px",
  },

  /** Status badges, severity chips — heaviest weight, no personality */
  tag: {
    fontVariationSettings: "'wght' 800, 'MONO' 0, 'CASL' 0, 'CRSV' 0.5, 'slnt' -3",
    fontSize: 11,
    letterSpacing: "1.5px",
  },

  /** Big numbers, KPI values — mono for alignment, casual for character */
  metric: {
    fontVariationSettings: "'wght' 400, 'MONO' 1, 'CASL' 0.6, 'CRSV' 0.5, 'slnt' 0",
    fontSize: 32,
    letterSpacing: "-0.5px",
  },

  /** Units after numbers — clinical mono */
  metricUnit: {
    fontVariationSettings: "'wght' 500, 'MONO' 1, 'CASL' 0, 'CRSV' 0.5, 'slnt' 0",
    fontSize: 13,
    letterSpacing: "0.5px",
  },

  /** Table cells, IP addresses, paths — full mono, no warmth */
  data: {
    fontVariationSettings: "'wght' 500, 'MONO' 1, 'CASL' 0, 'CRSV' 0.5, 'slnt' 0",
    fontSize: 13,
  },

  /** Inline code, commands, config — pure monospace */
  code: {
    fontVariationSettings: "'wght' 400, 'MONO' 1, 'CASL' 0, 'CRSV' 0.5, 'slnt' 0",
    fontSize: 13,
    letterSpacing: "0.5px",
  },

  /** Log times, durations */
  timestamp: {
    fontVariationSettings: "'wght' 500, 'MONO' 1, 'CASL' 0, 'CRSV' 0.5, 'slnt' 0",
    fontSize: 11,
    letterSpacing: "0.5px",
  },

  /** Sidebar navigation links — half-mono hybrid */
  nav: {
    fontVariationSettings: "'wght' 500, 'MONO' 0.5, 'CASL' 0.2, 'CRSV' 0.5, 'slnt' -2",
    fontSize: 14,
    letterSpacing: "1px",
  },

  /** Active sidebar link — bolder, slightly less casual */
  navActive: {
    fontVariationSettings: "'wght' 700, 'MONO' 0.5, 'CASL' 0.1, 'CRSV' 0.5, 'slnt' -2",
    fontSize: 14,
    letterSpacing: "1px",
  },

  /** Clickable links, actions — full italic, no casual */
  link: {
    fontVariationSettings: "'wght' 700, 'MONO' 0, 'CASL' 0, 'CRSV' 0.5, 'slnt' -15",
    fontSize: 10,
    letterSpacing: "1px",
  },

  /** Path navigation — mono italic with slight casual */
  breadcrumb: {
    fontVariationSettings: "'wght' 700, 'MONO' 1, 'CASL' 0.2, 'CRSV' 0.5, 'slnt' -7",
    fontSize: 10,
    letterSpacing: "2.5px",
  },
};

// ─── HELPERS ───────────────────────────────────────────────

/** Build fontVariationSettings from individual values */
export const fv = (wght, MONO, CASL, slnt = 0) =>
  `'wght' ${wght}, 'MONO' ${MONO}, 'CASL' ${CASL}, 'CRSV' 0.5, 'slnt' ${slnt}`;

/** Apply a type role as a style object */
export const applyType = (role) => ({
  fontFamily,
  fontVariationSettings: type[role].fontVariationSettings,
  fontSize: type[role].fontSize,
  ...(type[role].letterSpacing && { letterSpacing: type[role].letterSpacing }),
});

// ─── COLOR PALETTE (for reference) ─────────────────────────

export const colors = {
  bg: "#080b12",
  surface: "#0c111c",
  border: "#151e30",
  text: "#dce4ec",
  textMuted: "#6d85a0",   // 4.96:1 on surface ✅ AA
  textDim: "#4e6580",     // 3.14:1 — decorative only
  blue: "#38a0ff",        // Apparatus
  amber: "#e5a820",       // Crucible
  magenta: "#d946a8",     // Chimera
  green: "#18c760",
  red: "#ef4444",
};
