---
id: TASK-13
title: 'API: Expose Apparatus integration endpoints with test coverage'
status: Done
assignee:
  - codex
created_date: '2026-03-16 00:21'
updated_date: '2026-03-16 01:08'
labels:
  - feature
milestone: m-5
dependencies:
  - TASK-12
documentation:
  - >-
    /Users/nick/Developer/Chimera/backlog/docs/backlog.md/doc-2 -
    Apparatus-Integration-Checklist.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add the first public Chimera endpoints for the Apparatus integration in the existing integrations blueprint. This slice should cover status, recent history, and ghost traffic controls backed by focused backend tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 GET /api/v1/integrations/apparatus/status returns enabled, configured, reachable, baseUrl, health, and ghosts.
- [x] #2 GET /api/v1/integrations/apparatus/history returns a bounded history response suitable for UI display.
- [x] #3 POST ghost start and stop endpoints proxy to Apparatus and return stable JSON responses.
- [x] #4 Backend tests cover success, disabled config, missing config, timeout/network failure, and upstream error cases.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add Apparatus routes to the existing integrations blueprint using the shared service wrapper.
2. Define stable response contracts for status, history, and ghost controls.
3. Add focused backend tests with mocked upstream responses for success and failure paths.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented the Apparatus integration routes in `apps/vuln-api/app/blueprints/integrations/routes.py` using the shared `ApparatusService`. Added `GET /api/v1/integrations/apparatus/status`, `GET /api/v1/integrations/apparatus/history`, `POST /api/v1/integrations/apparatus/ghosts/start`, and `POST /api/v1/integrations/apparatus/ghosts/stop`.

The status endpoint intentionally returns a renderable 200 payload for disabled, misconfigured, and unreachable states so the Chimera UI can show state without treating the poll as a transport failure. History requests clamp invalid or zero limits back to `50` and cap large values at `500`. Ghost start also performs lightweight route-level payload validation for accepted top-level keys (`rps`, `duration`, `endpoints`) before proxying to Apparatus.

Added focused route coverage in `apps/vuln-api/tests/unit/test_integrations_routes.py` for status success/failure modes, history limit behavior, structured error responses, ghost start/stop passthrough, and invalid ghost-start payloads.

Verification: `cd apps/vuln-api && uv run pytest tests/unit/test_apparatus_service.py tests/unit/test_integrations_routes.py -v` (26 passed).

Independent review artifact: `.agents/reviews/review-20260315-210412.md`. Follow-up fixes from review included generic catch-all error hardening, zero-limit normalization, and lightweight ghost-start payload validation.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added the first backend Apparatus integration endpoints to Chimera's integrations blueprint. The new routes expose status, recent history, and ghost traffic controls via the shared service wrapper and return stable JSON for both healthy and degraded Apparatus states.

Focused backend coverage was added in `apps/vuln-api/tests/unit/test_integrations_routes.py`, bringing the combined Apparatus service and route suite to 26 passing tests with `cd apps/vuln-api && uv run pytest tests/unit/test_apparatus_service.py tests/unit/test_integrations_routes.py -v`.

Independent review artifact: `.agents/reviews/review-20260315-210412.md`. Commit: `a343634` (`feat(api): add apparatus integration endpoints`).
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
