# Week 6 — AI Code Review & Testing: The Habit Tracker

**Author**: Moha-Bishly  
**Repository**: [Moha-Bishly/AI-Augmented-Software-Engineering](https://github.com/Moha-Bishly/AI-Augmented-Software-Engineering)  
**Branch**: `week6-agentic-code-review`  
**AI Reviewer Used**: **CodeRabbit** (GitHub App)

---

## 1. Pull Requests & Implementation Overview

Two features were developed on dedicated feature branches, reviewed manually, tested, and opened as Pull Requests against the `week6-agentic-code-review` branch on GitHub with active CodeRabbit AI code reviews.

| Feature | Branch | Pull Request Link | Commit SHA |
| :--- | :--- | :--- | :--- |
| **Feature 1: Streak** | `feature/streak` | [PR #1: feat(streak)](https://github.com/Moha-Bishly/AI-Augmented-Software-Engineering/pull/1) | [`f6ef902`](https://github.com/Moha-Bishly/AI-Augmented-Software-Engineering/commit/f6ef902d75d79fb307d4e61dfae35716e2d54b46) |
| **Feature 2: Validation** | `feature/validation` | [PR #2: feat(validation)](https://github.com/Moha-Bishly/AI-Augmented-Software-Engineering/pull/2) | [`168cad6`](https://github.com/Moha-Bishly/AI-Augmented-Software-Engineering/commit/168cad622d3339587d1af5d43417608f9ff3d3e0) |

### PR Descriptions & Scope:
- **PR 1 (`GET /habits/{habit_id}/streak`)**: Computes the current run of consecutive days with check-ins up to and including today. Deduplicates multiple same-day check-ins using `SELECT DISTINCT day`, preserves active streaks if today is still pending check-in (streak ending yesterday), returns `404` for unknown habits, and allows deterministic date testing via `?today=YYYY-MM-DD`.
- **PR 2 (`Validation`)**: Rejects empty and whitespace-only habit names on `POST /habits` with HTTP `422`, and enforces strict ISO `YYYY-MM-DD` calendar date formatting on `POST /habits/{habit_id}/checkin` (rejecting non-dates, invalid calendar days like `2026-02-31`, unhyphenated dates, and empty payloads).

---

## 2. Deterministic Guardrails Setup

Deterministic guardrails serve as the first line of defense before any pull request is submitted or reviewed by human or AI agents.

### Tools & Commands
1. **Code Formatting (`black`)**:
   ```bash
   black --check assignments/06-agentic-code-review-and-testing/starter
   # Auto-format:
   black assignments/06-agentic-code-review-and-testing/starter
   ```
   - **What it catches**: Inconsistent indentation, quote style discrepancies (single vs double), non-standard line wraps, trailing comma inconsistencies, and unformatted SQL multi-line strings.

2. **Linting & Code Quality (`ruff`)**:
   ```bash
   ruff check assignments/06-agentic-code-review-and-testing/starter
   # Auto-fix safe issues:
   ruff check --fix assignments/06-agentic-code-review-and-testing/starter
   ```
   - **What it catches**: Unused imports, unsorted/unorganized import blocks (rule `I001`), undefined variables, deprecated idioms, and syntax antipatterns.

3. **Automated Unit Testing (`pytest`)**:
   ```bash
   pytest assignments/06-agentic-code-review-and-testing/starter
   ```
   - **What it catches**: Logical regressions, HTTP status code mismatches (e.g. 404 vs 422 vs 400), streak calculation errors, duplicate check-in inflation, and invalid calendar dates.
   - **Build Halt Verification**: During development of PR #2, an assertion checking for specific error substrings failed when Pydantic returned `'string_too_short'` instead of `'empty'`. `pytest` returned exit code `1` and immediately halted execution, confirming that broken tests reliably prevent unvalidated code from passing the build.

---

## 3. Human vs. AI Code Review Comparison

### PR 1: Streak Endpoint

#### Human Manual Review:
- **Domain Logic & Usability**: Examined the streak calculation logic for UX reality: if a user checks their streak in the morning before completing today's habit, their streak shouldn't abruptly display `0`. The code was adapted so that a streak ending yesterday remains active today until the day concludes.
- **Database Safety**: Noticed that the `checkins` table did not enforce a unique constraint on `(habit_id, day)`. Manually introduced `SELECT DISTINCT day` to prevent multiple check-ins on the same day from corrupting streak counts.
- **Testability**: Introduced an optional `today: str | None = None` query parameter to allow reproducible, deterministic unit tests across any future test date.

#### CodeRabbit AI Review:
- **Truthy vs. None Check (Line 112)**:
  > *"When a client sends `?today=`, `if today` selects `date.today()` instead of returning the documented 400 response for an invalid date. Use `if today is not None` so an empty value reaches the date parser."*
- **Test Gap Suggestion (Line 80)**:
  > *"Add a fixed-`today` test near `test_streak_with_custom_today_query_param` with check-ins yesterday and the day before, and no check-in today. Assert that the streak remains active through yesterday, covering the fallback behavior when today has no check-in."*

#### Comparative Analysis:
- **Where the AI was better**: The AI caught an exceptionally subtle Python semantics bug: `if today:` treats an explicitly supplied empty parameter (`?today=`) as falsy, silently falling back to `date.today()` instead of raising a `400 Bad Request`. The human developer had tested `?today=invalid-date` but overlooked `?today=`.
- **Where the Human was better**: The human developer correctly formulated the core business domain model (handling streak continuity when today is not yet checked in) and database-level deduplication (`DISTINCT`), which the AI accepted without questioning.

---

### PR 2: Validation

#### Human Manual Review:
- **Validation Architecture**: Replaced manual `if not name: raise HTTPException(400)` boilerplate with idiomatic Pydantic v2 field validators (`@field_validator`) and `Field(min_length=1)`.
- **Whitespace Sanitization**: Caught that strings with spaces only (`"   "`) pass `min_length=1`. Added `.strip()` check to raise `ValueError("habit name cannot be empty or whitespace only")`.
- **Calendar Parsing**: Ensured date validation catches impossible days (e.g., `2026-02-31` or month `13`) returning `422 Unprocessable Entity`.

#### CodeRabbit AI Review:
- **Python 3.11+ `date.fromisoformat` Loose Parsing**:
  > *"Reject day formats outside `YYYY-MM-DD`. On Python 3.11+, `date.fromisoformat` accepts `20260922` and ISO week dates without hyphens. The validator then returns a normalized date, so `POST /habits/{habit_id}/checkin` accepts these inputs instead of returning the stated 422 response. Check the exact `YYYY-MM-DD` shape before parsing."*
- **Dependency Version Pinning**:
  > *"Update the starter dependency declarations in requirements.txt to require `pydantic>=2,<3` so the `field_validator` import used by the application is available."*
- **Pre-Merge Docstrings**:
  > Flagged docstring coverage at 0% on new methods, advising standard PEP 257 docstrings.

#### Comparative Analysis:
- **Where the AI was better**: The AI uncovered an obscure change in Python 3.11's standard library where `date.fromisoformat` became more lenient (accepting compressed formats like `20260922` and week notations `2026-W39-2`). The human reviewer assumed `date.fromisoformat` only parsed standard `YYYY-MM-DD`.
- **Where the Human was better**: Designing the end-to-end integration and error contract with FastAPI/Pydantic, ensuring that clean, structured 422 payloads are returned instead of uncaught 500 crashes.

---

## 4. What You Learned

1. **Deterministic Guardrails are Non-Negotiable**: Linters (`ruff`), formatters (`black`), and test runners (`pytest`) provide instant, deterministic verification of syntax, style, and regression safety without token cost, latency, or hallucinations.
2. **AI Reviewers Excel at Obscure Edge Cases & Language Quirks**: Tools like CodeRabbit are remarkably effective at spotting subtle language-level edge cases that human reviewers frequently miss due to diff fatigue—such as Python 3.11's lenient `fromisoformat` parsing and `if value:` vs `if value is not None:` bugs.
3. **Defense-in-Depth Engineering**: AI review should neither replace deterministic unit tests nor eliminate human architectural oversight. The most robust workflow uses deterministic guardrails as the baseline barrier, human review for domain intent and API design, and AI review as an automated second pair of eyes to challenge assumptions and catch boundary oversights.
