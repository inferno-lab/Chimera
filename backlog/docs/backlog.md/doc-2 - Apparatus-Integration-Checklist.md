---
id: doc-2
title: Apparatus Integration Checklist
type: planning
created_date: '2026-03-16 00:19'
---

## Summary

Plan the first production-shaped Chimera to Apparatus integration as a service-to-service connection rather than a monorepo merge. Chimera web should talk to Chimera API, and Chimera API should act as the facade for Apparatus.

## Principles

- Keep Apparatus as a separate service and deployment unit.
- Use Chimera backend as the initial integration boundary.
- Do not consume `@apparatus/client` from Chimera frontend in the first slice.
- Scope the first milestone to status, ghost controls, history, UI surfacing, and docs.

## Execution Checklist

### 1. Confirm the integration boundary

- Keep Apparatus as a separate service.
- Make Chimera backend the facade; do not wire Chimera web directly to Apparatus yet.
- Reuse the existing integrations blueprint surface in `apps/vuln-api/app/blueprints/integrations/routes.py`.

### 2. Add backend config

- Add `APPARATUS_ENABLED`, `APPARATUS_BASE_URL`, and `APPARATUS_TIMEOUT_MS`.
- Default `APPARATUS_BASE_URL` to `http://127.0.0.1:8090`.
- Return a clean disabled response when integration is off.

### 3. Create the Python service wrapper

- Add `apps/vuln-api/app/services/apparatus_service.py`.
- Implement `get_status()`, `get_history(limit)`, `start_ghosts(payload)`, and `stop_ghosts()`.
- Use Python `requests` for upstream communication.
- Normalize timeout, network, and non-2xx errors into consistent Chimera JSON responses.

### 4. Add backend endpoints

- `GET /api/v1/integrations/apparatus/status`
- `GET /api/v1/integrations/apparatus/history?limit=50`
- `POST /api/v1/integrations/apparatus/ghosts/start`
- `POST /api/v1/integrations/apparatus/ghosts/stop`

### 5. Lock the response contracts

- `GET /status` returns `enabled`, `configured`, `reachable`, `baseUrl`, `health`, and `ghosts`.
- `GET /history` returns `count` and `entries`.
- `POST /ghosts/start` accepts `rps`, `duration`, and `endpoints`.
- `POST /ghosts/stop` returns a stop receipt or current ghost status.

### 6. Add backend tests

- Add `apps/vuln-api/tests/unit/test_integrations_routes.py`.
- Mock Apparatus success for health, history, start, and stop.
- Cover disabled config, missing base URL, timeout/network failure, and upstream 4xx/5xx cases.
- Verify JSON shape, not just status codes.

### 7. Add frontend API wrapper

- Add `apps/vuln-web/src/features/apparatus/api.ts`.
- Wrap only the Chimera endpoints for the first slice.
- Reuse the existing `useApi` and relative-path fetch patterns.

### 8. Add the first UI surface

- Add `apps/vuln-web/src/components/ApparatusPanel.tsx`.
- Mount it in `apps/vuln-web/src/pages/AdminDashboard.tsx`.
- Show connection state, ghost controls, recent history, and clean disabled/unreachable states.
- Do not embed the full Apparatus dashboard yet.

### 9. Add frontend tests

- Add component coverage for loading, connected, unreachable, and disabled states.
- Add button-action coverage for ghost start/stop.
- Verify empty-history rendering is stable.

### 10. Update docs

- Document env vars and local development flow in the repo docs.
- Explain that this is service-to-service integration, not a monorepo requirement.
- Add a local dev note for running Chimera alongside an external Apparatus instance.

### 11. Verify locally

- Run `make -C apps/vuln-api test-quick`.
- Run `pnpm nx run vuln-web:test`.
- Run `pnpm nx run vuln-web:build`.
- Manually smoke `status`, ghost start/stop, and history display against a live Apparatus instance.

### 12. Defer for phase 2

- SSE proxying of Apparatus `/sse`
- Scenario execution endpoints
- Deep dashboard embedding
- Direct `@apparatus/client` consumption in Chimera web

## Acceptance Criteria

- Chimera can report whether Apparatus is configured and reachable.
- Chimera can start and stop Apparatus ghost traffic.
- Chimera can display recent Apparatus history in the Admin UI.
- Chimera behaves cleanly when Apparatus is disabled or down.
- No monorepo dependency is introduced.

## Proposed Milestone

`m-5` - Apparatus Integration Foundation

### Candidate Tasks

- Backend config and Apparatus service wrapper
- Backend integration routes and test coverage
- Frontend Apparatus panel and API wiring
- Docs and local development guidance
