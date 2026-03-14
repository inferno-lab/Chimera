# Remaining Test Gaps: apps/vuln-web/src/components

The following test gaps were identified during the connectivity feature implementation and should be addressed in future workstreams.

## [P1] AI Assistant: File Upload Test
**File:** `apps/vuln-web/src/components/AiAssistant.test.tsx`
**Status:** Failing due to environment limitations.
**Description:** The test for file upload request construction is currently failing because JSDOM has limited support for the `File` object and `FormData` serialization in `fetch`.
**Suggested approach:** Use a more specialized mock for `FormData` or switch to a browser-based test (e.g., Playwright) for this specific interaction.

## [P1] WAF Visualizer: Logic & Animation
**File:** `apps/vuln-web/src/components/WafVisualizer.tsx`
**Severity:** P1
**Description:** The component contains complex simulation logic for the WAF pipeline that is currently untested.
**Suggested approach:** Create `WafVisualizer.test.tsx` and verify the state transitions of the visual pipeline when requests are processed.

## [P1] Kill Chain Tracker: Persistence & Matching
**File:** `apps/vuln-web/src/components/KillChainTracker.tsx`
**Severity:** P1
**Description:** The logic for matching attack logs to kill chain stages and persisting progress in `localStorage` is untested.
**Suggested approach:** Create `KillChainTracker.test.tsx`, mock `localStorage`, and verify that `chimera:attack-log` events correctly update the tracker state.

## [P2] Remaining UI Components
**Module:** `apps/vuln-web/src/components`
**Description:** Several smaller UI components (`HintChip`, `ComingSoon`, `VulnerabilityModal`) have no test coverage.
**Suggested approach:** Add simple smoke tests to verify rendering and basic prop handling.
