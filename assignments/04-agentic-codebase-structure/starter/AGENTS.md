# Agent Guidance — Link Shortener

A lightweight URL shortener service built with FastAPI and SQLite.

## Project Structure
- `main.py`: Core FastAPI service, database initialization, URL encoding, and route handlers.
- `test_main.py`: Behavioral test suite using FastAPI's `TestClient`.
- `docs/TASKS.md`: Feature roadmap and extension choices.
- `requirements.txt`: Python package dependencies.
- `links.db`: SQLite database file (created automatically; git-ignored).

## Commands
```bash
# Setup
pip install -r requirements.txt

# Run test suite
pytest

# Start local development server
uvicorn main:app --reload
```

## Product Boundaries
- **In Scope**:
  - URL validation (`http://` or `https://` prefix requirement).
  - Clean HTTP status codes (200, 307 redirect, 400 bad input, 404 not found, 409 conflict, 410 expired).
  - Compact, single-file service architecture backed by standard SQLite.
- **Out of Scope**:
  - Frontend UI, authentication, external database drivers, background queue workers.

## Change Workflow
Follow this disciplined cycle for all code modifications:
1. **Understand**: Clarify requirements against `docs/TASKS.md` and inspect `main.py`.
2. **Test**: Write a failing behavioral test asserting expected HTTP response status and payload.
3. **Implement**: Make the smallest clean change to satisfy the test.
4. **Verify**: Run `pytest` to confirm all existing and new tests pass with zero regressions.
