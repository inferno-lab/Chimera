---
id: TASK-1
title: Repair local dev startup targets for API and web
status: Done
assignee:
  - nferguson
created_date: '2026-03-12 03:38'
updated_date: '2026-03-12 03:47'
labels:
  - bug
  - developer-experience
dependencies: []
references:
  - /Users/nferguson/Developer/Security Lab Suite/Chimera/justfile
  - >-
    /Users/nferguson/Developer/Security Lab
    Suite/Chimera/apps/vuln-api/project.json
  - /Users/nferguson/Developer/Security Lab Suite/Chimera/apps/vuln-api/Makefile
  - /Users/nferguson/Developer/Security Lab Suite/Chimera/README.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The documented local development commands should start the Flask API and React dev server through `just` and direct `pnpm nx` invocations. At the moment the API startup path is broken because the just recipes reference the wrong Nx project name and the API Nx `start` target points at nonexistent Make targets. Update the command wiring so the documented dev entry points work as described.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `just api-start` launches the API using the configured Nx target without an immediate configuration failure.
- [x] #2 `just dev` and equivalent direct `pnpm nx` commands resolve the correct project names for both the API and web apps.
- [x] #3 Project documentation for local startup commands matches the verified command paths.
- [x] #4 Relevant targeted verification is captured in the task notes and final response.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update the Nx-facing command wiring so the API project name and target commands match the actual repo configuration.
2. Align the `just` recipes and README examples with the verified Nx project names and startup targets.
3. Re-run the broken startup commands just far enough to confirm they now resolve and launch instead of failing on missing project/target configuration.
4. Run targeted build/test checks for touched config/docs files and record the evidence in task notes before closing.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Investigated the original failures and reproduced two startup blockers: `pnpm nx run vuln-api:start` failed because the Nx project is actually named `chimera-api`, and `pnpm nx run chimera-api:start` failed because the target called nonexistent `make start`/`make stop` recipes.

Aligned the dev startup contract on port 8880 after confirming port 5000 is already occupied in this environment and Vite could not proxy cleanly to the API there.

Updated the API Makefile to invoke Gunicorn as `python -m gunicorn`, which resolved `uv run gunicorn` failing with `No such file or directory`.

Scoped external review via `specialist-review.sh` flagged an incorrect README port comment and a risky `app.py` default-port change; both were corrected before finalizing. Review verdict after remediation was `APPROVE WITH CHANGES` with remaining minor follow-up observations only.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Repaired the local startup path for the Chimera API and web app by aligning Nx, just, and Vite on the repo’s actual API project name and verified dev port. The `just` recipes now target `chimera-api`, the API Nx `start` target runs the existing foreground dev server on port 8880, and the Vite proxy plus top-level startup docs now point to that same port. I also changed the API Makefile to launch Gunicorn via `python -m gunicorn`, which fixed the runtime failure where `uv run gunicorn` could not spawn the executable in this environment.

Verification: `pnpm nx show projects` returned `chimera-api` and `vuln-web`; `just api-start` reached a live Gunicorn listener on `http://0.0.0.0:8880`; `just dev` launched both Nx start targets concurrently; `curl -sSf http://localhost:8880/api/v1/healthz` returned `{"status":"healthy"}`; `curl -I -s http://localhost:5176` returned `HTTP/1.1 200 OK` while Vite was running. Scoped external review was run twice with `specialist-review.sh` and the review-driven fixes were applied.

Residual risk: `pnpm nx run vuln-web:build` still fails because of pre-existing TypeScript/test issues in already-modified web files such as `src/components/AiAssistant.test.tsx`, `src/components/Connectivity.test.tsx`, `src/components/RequestInspectorProvider.tsx`, and `src/hooks/useTypography.ts`. Those failures predated this startup wiring change and were not modified here.
<!-- SECTION:FINAL_SUMMARY:END -->
