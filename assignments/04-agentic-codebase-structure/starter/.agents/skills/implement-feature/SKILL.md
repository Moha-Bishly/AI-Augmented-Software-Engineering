---
name: implement-feature
description: Guide the implementation of a new feature in the link shortener following test-driven development and agent-ready repository guidelines.
---

# Feature Implementation Workflow

Follow this 7-step procedure whenever implementing an endpoint or feature in this repository:

## Step 1: Read Task & Repository Context
- Consult `AGENTS.md` for project boundaries and architectural style.
- Review the selected specification in `docs/TASKS.md`.

## Step 2: Inspect Existing Implementation
- Inspect `main.py` for route handlers, database schema, and helper utilities.
- Inspect `test_main.py` for testing patterns and fixtures.

## Step 3: State Expected Behavior & Scope
- Formulate the expected contract: HTTP route, method, request schema, status codes, and response JSON.
- Identify all affected files before making changes.

## Step 4: Add Failing Behavioral Test
- In accordance with `tests/AGENTS.md`, write test cases using `TestClient`:
  - Happy path / success case.
  - Negative path / validation or conflict failure case.
- Run `pytest` and verify that the new test fails for the expected reason (Red stage).

## Step 5: Implement Minimal Clean Solution
- Implement the simplest code changes in `main.py` that fulfill the requirements.
- Maintain error handling consistency (e.g. `HTTPException`).

## Step 6: Verify with Pytest
- Execute `pytest` across the entire test suite.
- Confirm all new tests pass and all previous tests remain green (Green stage).

## Step 7: Summary & Risk Assessment
- Provide a concise summary of changes made.
- Note any potential edge cases, migration needs, or operational risks.
