---
id: TASK-16.2
title: 'Migrate Tier 3 blueprints (session-using, 5 blueprints)'
status: In Progress
assignee: []
created_date: '2026-04-12 04:07'
updated_date: '2026-04-16 19:25'
labels:
  - refactor
dependencies: []
parent_task_id: TASK-16
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the codemod on 5 Tier 3 blueprints that use Flask session state, and verify the session migration path to Starlette's SessionMiddleware works correctly.

## Blueprints
- education (73 lines) — `session.get('user_id')`
- checkout (124 lines) — `session.get('session_id')`
- mobile (146 lines) — `session.get('user_id')`
- saas (567 lines) — `session['tenant_id']`
- payments (683 lines) — `session.get('customer_id')`

## Session handling
The codemod already rewrites `session['key']` → `request.session['key']` and `session.get(...)` → `request.session.get(...)`. Starlette's SessionMiddleware (already configured in app/asgi.py with cfg.secret_key) stores session data in a signed cookie — same mechanism Flask uses by default.

## Process
Same as Tier 2, but verify session behavior:
1. Run codemod
2. Manual review for session keys and any session.pop() / session.clear() calls
3. Update __init__.py and wire into asgi.py
4. Smoke test a session-requiring flow (e.g., login → authenticated endpoint)

## Gotchas
- Session cookies from Flask won't be readable by Starlette unless the secret_key matches — they use different signing algorithms. Fresh login required on cutover.
- Any blueprint-level `@bp.before_request` hooks (e.g., education/routes.py:12 `check_access()`) need manual conversion to Starlette middleware or moved into the handler body.

## Reference
- Tier 1 reference commit: 990741b
- Tier 2 subtask: TASK-16.1
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All 5 Tier 3 blueprints transformed by codemod
- [ ] #2 Session state correctly flows through request.session
- [ ] #3 education check_access hook converted (to middleware or inline)
- [ ] #4 Flask factory no longer imports Tier 3 blueprints
- [ ] #5 Session-requiring endpoint smoke tests pass on uvicorn
- [ ] #6 Flask test suite still passes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Finish the remaining Tier 3 wave by migrating saas and payments, then run a uvicorn smoke flow that exercises session-backed endpoints across both blueprints before checking off the task acceptance criteria.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-04-16: Migrated the first Tier 3 wave to Starlette (education, checkout, mobile). Flask create_app() now mirrors these routers through register_flask_compat_routes, and app/asgi.py mounts them natively alongside the earlier waves.

Session migration coverage added via signed SessionMiddleware cookies in tests/conftest.py, including localhost-vs-remote education gate coverage and Flask/ASGI parity for checkout/mobile session flows.

Verification receipts: focused slice `cd apps/vuln-api && uv run pytest tests/unit/test_education_routes.py tests/unit/test_checkout_routes.py tests/unit/test_mobile_routes.py tests/unit/test_migrated_flask_compat_routes.py tests/unit/test_routing.py -q` -> 56 passed; broader regression `cd apps/vuln-api && uv run pytest tests/unit -q` -> 734 passed, 1 skipped.

Independent review artifacts: .agents/reviews/review-20260416-150902.md, review-20260416-151138.md, review-20260416-151440.md, review-20260416-151801.md. Remaining blocked findings are mostly review-context false positives plus a follow-on design preference around making the education access gate structural instead of decorator-based.

Independent test audit artifact: .agents/reviews/test-audit-20260416-152121.md. Audit highlights broad inherited module coverage debt; for this migration slice, the newly added coverage locks in session flow, localhost-vs-remote auth behavior, malformed cart-state handling, and Flask/ASGI parity for the migrated endpoints.
<!-- SECTION:NOTES:END -->
