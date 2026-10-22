# Week 4 Reflection — Agentic Codebase Structure

## 1. Root Guidance in `AGENTS.md`
In the root `AGENTS.md`, I included high-level orientation: a concise summary of the application (a FastAPI and SQLite URL shortener), key file locations, essential terminal commands (installation, running tests, local server startup), architectural product boundaries, and a core four-step development workflow (Understand, Test, Implement, Verify). This guidance is broadly available across the entire workspace because any agent beginning an unfamiliar task needs immediate context on how the project builds, runs, and enforces boundaries without guessing commands or introducing unwanted dependencies.

## 2. Scoped Instruction and Activation
I placed a scoped instruction in `tests/AGENTS.md` (mirrored in `.agents/rules/testing.md`). This instruction only activates when authoring, modifying, or evaluating test files (`test_*.py` or files within the `tests/` directory). It mandates testing through the public API via FastAPI's `TestClient`, enforcing both happy-path and negative error coverage, maintaining test isolation, and verifying behavioral outcomes rather than internal state. This is kept scoped because detailed test policies clutter context during unrelated feature coding, refactoring, or documentation tasks.

## 3. Reusable Workflow Procedure
The reusable workflow in `.agents/skills/implement-feature/SKILL.md` encodes a disciplined 7-step test-driven development procedure:
1. Review task specifications and repository context.
2. Inspect existing route implementations and test patterns.
3. Explicitly declare expected contract and impacted files before editing.
4. Add a failing behavioral test asserting both success and failure cases (Red stage).
5. Implement the minimal clean code in `main.py` to satisfy the specification.
6. Run the complete pytest suite to verify all tests pass (Green stage).
7. Summarize the changes and evaluate risks.

## 4. Discovery and Tool Mapping
My selected coding agent, Antigravity, discovers and applies these artifacts through standard mechanisms:
- **`AGENTS.md`**: Loaded automatically into context as the repository-level baseline.
- **`tests/AGENTS.md` & `.agents/rules/testing.md`**: Automatically matched and loaded whenever the agent accesses test files matching the glob pattern `["test_*.py", "tests/**"]`.
- **`implement-feature` Skill**: Placed in `.agents/skills/implement-feature/SKILL.md` following the Agent Skills standard, making it invokable as a reusable command during implementation.

## 5. Planning and Review Insights
During planning, inspecting the schema revealed that SQLite already enforced a `UNIQUE` constraint on `code`. The plan identified that querying for existing codes prior to insertion allowed returning an explicit HTTP 409 Conflict rather than crashing with an unhandled database exception. During review, running consecutive test passes exposed a state leak: SQLite persisted records to disk between test invocations, causing subsequent runs to trigger unexpected 409 collisions. Guided by the test-isolation principle in `tests/AGENTS.md`, I introduced an autouse fixture in `test_main.py` that clears test rows, ensuring repeatable and isolated test runs.

## 6. Structuring Repositories for Coding Agents
Structuring a codebase for agents requires layered context rather than monolithic prompts. A compact root file prevents prompt bloat while defining firm boundaries. Scoped rules ensure specialized rules load only when relevant, and reusable workflows enforce deterministic development habits like TDD. This structure enables agents to work autonomously with high precision and low regression risk.
