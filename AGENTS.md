# Repository Guidelines

## Project Structure & Module Organization
- `backend/` holds the Python service. Core app code lives in `backend/app/` with subfolders for `api/`, `core/`, `modules/`, and `services/`.
- Domain modules follow a consistent pattern under `backend/app/modules/<domain>/` (e.g., `models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`).
- Tests are under `backend/tests/` with subfolders like `api/` and `modules/`.
- `frontend/` and `infra/` exist but are currently empty placeholders.

## Build, Test, and Development Commands
- Backend runs are currently minimal; for now you can execute the sample entrypoint:
  - `python backend/main.py` (prints a hello message).
- Typical FastAPI dev run once an app object is added (example):
  - `uvicorn app.main:app --reload --app-dir backend`
- Dependency management appears to use `uv` (`backend/uv.lock`):
  - `uv sync` (install deps)
  - `uv run pytest` (run tests)

## Coding Style & Naming Conventions
- Python uses 4-space indentation; keep modules and packages `snake_case`.
- Domain module filenames should stay consistent: `models.py`, `schemas.py`, `service.py`, `repository.py`, `router.py`.
- `ruff` is included in dev dependencies; use it for linting/formatting when configured:
  - `ruff check backend`

## Testing Guidelines
- Tests use `pytest` with `pytest-asyncio` available for async tests.
- Prefer naming tests `test_*.py` and test functions `test_*`.
- Run all tests from the repo root:
  - `uv run pytest backend/tests`

## Commit & Pull Request Guidelines
- Existing history uses Conventional Commits with scope (e.g., `feat(backend): ...`); follow that pattern for consistency.
- PRs should include a short description, key changes, and any relevant screenshots or logs if behavior changes.

## Configuration & Security Tips
- Copy `.env.example` to `.env` for local settings and never commit real secrets.
- Docker files are present in `backend/`, but `docker-compose.yml` is currently empty; update as needed for local orchestration.
