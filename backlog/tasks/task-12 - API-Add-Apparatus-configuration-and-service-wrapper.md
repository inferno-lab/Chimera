---
id: TASK-12
title: 'API: Add Apparatus configuration and service wrapper'
status: Done
assignee:
  - codex
created_date: '2026-03-16 00:21'
updated_date: '2026-03-16 00:47'
labels:
  - feature
milestone: m-5
dependencies: []
documentation:
  - >-
    /Users/nick/Developer/Chimera/backlog/docs/backlog.md/doc-2 -
    Apparatus-Integration-Checklist.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add the backend configuration surface and Python service wrapper needed for Chimera to communicate with an external Apparatus instance. This task should establish the reusable upstream client boundary but not yet expose new user-facing routes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 APPARATUS_ENABLED, APPARATUS_BASE_URL, and APPARATUS_TIMEOUT_MS are wired into the backend with sensible defaults.
- [x] #2 A Python Apparatus service wrapper exposes status, history, ghost start, and ghost stop helpers.
- [x] #3 Timeout, network, and upstream non-2xx failures are normalized into stable Chimera-side error handling.
- [x] #4 Implementation references the planning doc for the initial integration scope.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add backend configuration reads and defaults for Apparatus connectivity.
2. Implement a reusable Python service wrapper around the required Apparatus HTTP endpoints using requests.
3. Normalize failure cases so the route layer can return stable JSON responses.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Apparatus backend foundation in two parts: app config wiring in apps/vuln-api/app/__init__.py and a new Python service wrapper in apps/vuln-api/app/services/apparatus_service.py with exported symbols in app/services/__init__.py.

Added focused unit coverage in apps/vuln-api/tests/unit/test_apparatus_service.py for default settings, invalid and non-positive timeout handling, disabled integration, missing base URL, network timeout/request failures, status fetch, history limiting, and upstream error propagation.

Verification: `cd apps/vuln-api && uv sync --extra dev`; `cd apps/vuln-api && uv run pytest tests/unit/test_apparatus_service.py -v` (10 passed).

Independent review artifacts: `.agents/reviews/review-20260315-204212.md`, `.agents/reviews/review-20260315-204354.md`, `.agents/reviews/review-20260315-204531.md`. Review findings led to explicit timeout normalization and base URL trimming.

Independent test audit artifact: `.agents/reviews/test-audit-20260315-204212.md`. Claude's first audit output failed the contract and Gemini provided the normalized artifact. The audit primarily surfaced broader app-factory coverage gaps in apps/vuln-api/app/__init__.py rather than new service-wrapper gaps; no additional TASK-12-specific blocker was identified.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added the backend foundation for Chimera's Apparatus integration. `create_app()` now records Apparatus enablement, base URL, and timeout config in app config, and the new `app.services.apparatus_service` module provides a reusable Python wrapper for status, history, and ghost traffic calls with normalized disabled/config/network/upstream error types.

Focused unit coverage was added in `apps/vuln-api/tests/unit/test_apparatus_service.py` for settings normalization, service success paths, and failure handling. Verification passed with `cd apps/vuln-api && uv run pytest tests/unit/test_apparatus_service.py -v` (10 passed).

Independent review artifacts: `.agents/reviews/review-20260315-204212.md`, `.agents/reviews/review-20260315-204354.md`, `.agents/reviews/review-20260315-204531.md`. Independent test audit artifact: `.agents/reviews/test-audit-20260315-204212.md` (Gemini normalized after a Claude contract miss). Commit: `3145d5f` (`feat(api): add apparatus service foundation`).
<!-- SECTION:FINAL_SUMMARY:END -->
