# Repository Guidelines

## Project Structure & Ownership
- `app/`: Flask code split by blueprint domains (`blueprints/`), data layer (`models/`), and helpers (`utils/`).
- `tests/`: Unit (`tests/unit`), integration (`tests/integration`), and security/vulnerability suites (`tests/vulnerability`, `tests/smoke`).
- `docs/` and `API-DOCUMENTATION.md`: Endpoint reference and contributor notes; update when adding routes or payload examples.
- `static/`: Demo assets served by Flask; keep large files out of git.
- Entrypoints: `app.py` for local dev, `wsgi.py`/`gunicorn.conf.py` for deployment.

## Build, Run, and Dev Workflow
- `uv sync --extra dev --frozen`: Install Python 3.12 deps into `.venv` (preferred, matches Docker).
- `PORT=8880 uv run python app.py`: Launch locally in vulnerable mode on port 8880.
- `USE_DATABASE=true uv run python app.py`: Enable SQLite-backed SQLi scenarios.
- `just run` / `just run-vulnerable`: Gunicorn with `DEMO_MODE=full` (intentionally unsafe).
- `just run-secure`: Hardened mode (`DEMO_MODE=strict`) for control comparisons.
- Docker: `docker build -t demo-api .` then `docker run -p 8080:80 demo-api` (honors `USE_DATABASE` env var).

## Testing Guidelines
- Default: `just test` (delegates to `./run_tests.sh all`).
- Fast feedback: `just test-quick` or `just test-unit`.
- Security focus: `just test-vulnerability` (pytest `-m vulnerability`), smoke checks via `just test-smoke`.
- Coverage: `just test-coverage` (fails <80%); HTML report via `just test-report` → `reports/test_report.html`.
- Naming: use `test_<feature>.py` and pytest-style functions; place fixtures near consuming tests or under `tests/conftest.py`.

## Coding Style & Tooling
- Formatting: `just format` (black, 120-char lines). Linting: `just lint` (flake8 + pylint; docstring warnings disabled). Fix style before pushing.
- Prefer explicit imports, typed function signatures where feasible, and small, isolated fixtures for new vulnerabilities.
- Configuration via env vars: `DEMO_MODE` (`full` vs `strict`), `USE_DATABASE` (enable SQLi), plus feature toggles in `security.py`.

## Commit & PR Expectations
- Follow Conventional Commits seen in history, e.g., `feat(api)`, `refactor(load-testing)`, `docs(readme)` with scope where meaningful.
- PRs should include: problem statement, summary of changes, relevant `just`/`uv run` commands executed, and screenshots or curl samples for new endpoints.
- Keep changes small and grouped by domain blueprint; update docs and tests in the same PR.

## Security & Safe Handling
- This app is intentionally vulnerable; never point at production data or networks.
- Run demos in isolated environments, and explicitly set `DEMO_MODE=strict` when showcasing mitigations.
- Rotate and avoid committing secrets; prefer env vars and keep `.env` files out of version control.
