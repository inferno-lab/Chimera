---
id: TASK-10
title: Resolve current vuln-web TypeScript build failures
status: Done
assignee:
  - nferguson
created_date: '2026-03-12 04:27'
updated_date: '2026-03-12 04:29'
labels:
  - bug
  - frontend
  - typescript
dependencies: []
references:
  - >-
    /Users/nferguson/Developer/Security Lab
    Suite/Chimera/apps/vuln-web/src/components/ConnectivityStatus.tsx
  - >-
    /Users/nferguson/Developer/Security Lab
    Suite/Chimera/apps/vuln-web/src/components/RequestInspectorProvider.tsx
  - >-
    /Users/nferguson/Developer/Security Lab
    Suite/Chimera/apps/vuln-web/src/components/AiAssistant.test.tsx
  - >-
    /Users/nferguson/Developer/Security Lab
    Suite/Chimera/apps/vuln-web/src/components/Connectivity.test.tsx
  - >-
    /Users/nferguson/Developer/Security Lab
    Suite/Chimera/apps/vuln-web/src/hooks/useTypography.ts
  - >-
    /Users/nferguson/Developer/Security Lab
    Suite/Chimera/apps/vuln-web/src/lib/type-system.js
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The current `pnpm nx run vuln-web:build` flow fails during TypeScript compilation in tests, connectivity components, request inspector fetch interception, and the typography hook/module bridge. Fix the TypeScript errors so the web build can complete cleanly again.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `pnpm nx run vuln-web:build` completes without TypeScript compilation errors.
- [x] #2 Connectivity and request-inspector code compile without `TS2556` or unused-symbol failures.
- [x] #3 Test files compile without relying on undeclared `global` symbols.
- [x] #4 The typography hook/module bridge has a valid TypeScript type surface.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Reproduce the current `vuln-web` build failure to capture the active TypeScript errors.
2. Fix the failing test files by removing unused React imports and replacing undeclared `global` references with browser-safe globals.
3. Repair component typing issues in connectivity/request-inspector code and add a declaration surface for the typography module bridge.
4. Re-run `pnpm nx run vuln-web:build`, capture the successful result, then close the task with any residual risks noted.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Reproduced the build failure with `pnpm nx run vuln-web:build` and confirmed the active TypeScript issues were limited to test globals, unused React/icon imports, request-inspector fetch argument typing, and the missing declaration surface for `src/lib/type-system.js`.

Fixed the test failures by switching from undeclared `global` references to `globalThis.fetch` and removing unused React imports from the Vitest files.

Fixed component typing by removing unused connectivity icons/helpers, updating the connectivity footer URL to the current backend port, and typing the request-inspector fetch wrapper as `Parameters<typeof fetch>`/`Promise<Response>`.

Added `src/lib/type-system.d.ts` so `useTypography.ts` can import the JS typography module with a real TypeScript contract.

Scoped review shell-out failed because the Claude CLI hit its usage limit; the partial artifact at `.agents/reviews/review-20260312-002922.md` only contains the limit message, so local verification receipts are the source of truth for this task.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Resolved the `vuln-web` TypeScript build failures across the current connectivity, request-inspector, test, and typography files. The Vitest files now use `globalThis.fetch` and no longer import unused React bindings, `ConnectivityStatus` no longer carries unused symbols, `RequestInspectorProvider` wraps `fetch` with the real `fetch` tuple signature, and a new `src/lib/type-system.d.ts` file provides a typed surface for the existing JS typography module.

Verification: `pnpm nx run vuln-web:build` now completes successfully and reaches the Vite production build step without TypeScript compiler errors. Residual note: the scoped external review request failed because the Claude CLI hit its rate/usage limit, and the saved artifact contains only the limit message, so review coverage for this task is unavailable beyond local verification.
<!-- SECTION:FINAL_SUMMARY:END -->
