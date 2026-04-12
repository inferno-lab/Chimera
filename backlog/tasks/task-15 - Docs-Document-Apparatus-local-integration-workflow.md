---
id: TASK-15
title: 'Docs: Document Apparatus local integration workflow'
status: Done
assignee:
  - codex
created_date: '2026-03-16 00:21'
updated_date: '2026-03-16 01:12'
labels:
  - documentation
milestone: m-5
dependencies:
  - TASK-13
  - TASK-14
documentation:
  - >-
    /Users/nick/Developer/Chimera/backlog/docs/backlog.md/doc-2 -
    Apparatus-Integration-Checklist.md
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Document how to run Chimera with an external Apparatus instance once the first integration slice lands. Capture the environment variables, local startup expectations, and the service-to-service architecture decision so the integration is repeatable for future contributors.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Repo docs describe the Apparatus integration architecture as service-to-service rather than monorepo coupling.
- [x] #2 Environment variables and default local Apparatus base URL are documented.
- [x] #3 Local development steps cover running Chimera alongside an external Apparatus instance and exercising the integration endpoints or UI.
- [x] #4 Documentation references the planning doc and the implemented integration surface.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update the appropriate repo docs with Apparatus integration architecture and env var guidance.
2. Add local development steps for running Chimera with a separate Apparatus service.
3. Verify the docs reflect the final implemented endpoint and UI surface.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated `README.md` with a dedicated "Local Development With Apparatus" section that documents the service-to-service architecture, the new backend environment variables, the default local Apparatus URL, and the initial integration endpoints/UI surface.

Updated `docs/developer-guide.md` to fix the stale `just dev` API port from `5000` to `8880`, add a new "Run With Apparatus" workflow, include smoke-test `curl` commands for the integration endpoints, and reference the planning checklist at `backlog/docs/backlog.md/doc-2 - Apparatus-Integration-Checklist.md`.

Verification was done by checking the documented routes and UI targets against the live source files: `apps/vuln-api/app/__init__.py`, `apps/vuln-api/app/blueprints/integrations/routes.py`, `apps/vuln-web/src/App.tsx`, and `apps/vuln-web/src/components/ApparatusPanel.tsx`.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Documented the Apparatus integration in both the top-level README and the developer guide. The docs now explain that Chimera talks to Apparatus as an external service, list the `APPARATUS_*` environment variables, show local startup commands, and point contributors at the new admin panel and integration endpoints.

The developer guide also now reflects the real `just dev` API port (`8880`) instead of the stale `5000` value.

Commit: `dddd66b` (`docs(readme): add apparatus integration workflow`).
<!-- SECTION:FINAL_SUMMARY:END -->
