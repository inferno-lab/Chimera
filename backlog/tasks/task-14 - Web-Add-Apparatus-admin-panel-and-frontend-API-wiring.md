---
id: TASK-14
title: 'Web: Add Apparatus admin panel and frontend API wiring'
status: Done
assignee:
  - codex
created_date: '2026-03-16 00:21'
updated_date: '2026-03-16 01:09'
labels:
  - feature
milestone: m-5
dependencies:
  - TASK-13
documentation:
  - >-
    /Users/nick/Developer/Chimera/backlog/docs/backlog.md/doc-2 -
    Apparatus-Integration-Checklist.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Surface the first Apparatus integration controls in Chimera web by adding a compact admin-facing panel backed by Chimera API endpoints. The initial panel should focus on connection state, ghost controls, and recent history without embedding the full Apparatus dashboard.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A frontend API wrapper calls the Chimera Apparatus endpoints for status, history, ghost start, and ghost stop.
- [x] #2 AdminDashboard renders an Apparatus panel with connected, disabled, unreachable, and loading states.
- [x] #3 The panel exposes ghost start/stop controls and renders recent Apparatus history.
- [x] #4 Frontend tests cover the main view states and ghost action flows.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a small frontend API module for the Chimera Apparatus facade endpoints.
2. Build an Apparatus panel component and mount it in AdminDashboard.
3. Add component tests for states and user actions.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added a small frontend Apparatus facade in `apps/vuln-web/src/features/apparatus/api.ts` and the new `apps/vuln-web/src/components/ApparatusPanel.tsx` component for status, ghost controls, and recent history. The panel is mounted into `apps/vuln-web/src/pages/AdminDashboard.tsx` as a full-width admin card.

While wiring the panel, `AdminDashboard.tsx` also picked up a few low-risk cleanup improvements in the touched area: typed defense toggle keys, typed audit log entries, accessible switch semantics for the existing defense toggles, and stable keys/runtime guards for audit log rendering.

Added focused component coverage in `apps/vuln-web/src/components/ApparatusPanel.test.tsx` for connected, disabled, and unreachable states plus ghost start/stop actions.

Verification: `COREPACK_ENABLE_AUTO_PIN=0 pnpm nx run vuln-web:test -- --run src/components/ApparatusPanel.test.tsx` (5 passed).

Residual verification note: `COREPACK_ENABLE_AUTO_PIN=0 pnpm nx run vuln-web:build` still fails on unrelated pre-existing frontend issues in `src/components/RequestInspectorProvider.tsx`, `src/hooks/useVulnerabilityInfo.ts`, `src/pages/IcsOtDashboard.tsx`, and `src/pages/LoyaltyDashboard.tsx`. No current build failures point at the Apparatus files touched in this task.

Independent review artifact: `.agents/reviews/review-20260315-210632.md`. Follow-up fixes from review added a focus-visible ring for the switch controls and a runtime guard plus stable key for audit logs.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added the first Chimera web surface for Apparatus: a new `ApparatusPanel` in Admin Dashboard backed by a dedicated frontend API module. The panel shows Apparatus connection state, lets an admin start or stop ghost traffic, and renders recent request history from the new Chimera backend endpoints.

Focused UI coverage was added in `apps/vuln-web/src/components/ApparatusPanel.test.tsx`, and the targeted test pass succeeded with `COREPACK_ENABLE_AUTO_PIN=0 pnpm nx run vuln-web:test -- --run src/components/ApparatusPanel.test.tsx` (5 passed).

The full `vuln-web` build still fails, but only on unrelated pre-existing files outside the Apparatus slice (`RequestInspectorProvider.tsx`, `useVulnerabilityInfo.ts`, `IcsOtDashboard.tsx`, `LoyaltyDashboard.tsx`). Commit: `9aeb423` (`feat(web): add apparatus admin panel`).
<!-- SECTION:FINAL_SUMMARY:END -->
