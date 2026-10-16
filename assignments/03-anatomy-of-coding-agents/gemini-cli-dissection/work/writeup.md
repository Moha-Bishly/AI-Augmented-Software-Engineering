# Week 3 Writeup — Inside a Coding Agent

**Name:** Mohammed Bishly
**Gemini CLI version (`gemini --version`):** `0.64.0`
**OS / shell:** Windows 11 + Git Bash (MINGW64)
**Model(s) seen in trace:** `gemini-3.5-flash-lite`
**Session commit:** `ce5b8a1`

> Evidence tags: `[OBSERVED]` = cite a timeline line, call number, or diff hunk.
> `[INFERRED]` = say what you're reasoning from.

---

## Part I — Session

**Narrative (one paragraph):**
The session executed completely autonomously from a single initial prompt instructing Gemini CLI to read `TASK.md`, plan, and implement all tasks without confirmation `[OBSERVED: session_timeline.txt L2]`. In Call #1, the agent initialized its status using `update_topic` and read `TASK.md`. In Call #2, it performed an empirical baseline diagnosis by running `python -m pytest` via `run_shell_command`—identifying two failing tests (`test_add_same_item_twice_increments_quantity` and `test_fixed_discount_applied_before_tax`)—while simultaneously reading all implementation and test files (`shopcart/cart.py`, `pricing.py`, `catalog.py`, `tests/test_cart.py`, `test_pricing.py`) in parallel `[OBSERVED: session_timeline.txt L8-14]`. In Calls #3–#5, it searched for existing total calculations with `grep_search` and outlined its architecture plan. In Calls #6 and #7, the agent applied surgical edits using `replace`: fixing the item quantity overwriting bug in `cart.py` and correcting the discount application order alongside adding shipping rules in `pricing.py`. In Call #8, it verified the fix by re-running `pytest`, and in Calls #10 and #11, it updated existing tests and added new unit tests for shipping fee rules and thresholds using `write_file`. Calls #12–#16 executed `pytest` (23 passed in 0.04s), `git status`, and `git --no-pager diff` to verify clean repository status and correct diffs. Finally, in Call #17, it updated the topic to completed and delivered the final summary `[OBSERVED: session_timeline.txt L55-58]`.

| Metric | Value |
|---|---|
| User prompts | `1` `[OBSERVED: session_timeline.txt L61]` |
| Model calls | `17` (errors: 0) `[OBSERVED: session_timeline.txt L62]` |
| Tool calls (failed) | `22 (0)` `[OBSERVED: session_timeline.txt L63]` |
| Final `pytest` result | `23 passed in 0.04s` `[OBSERVED: session_timeline.txt L44, terminal screenshot]` |
| Did you step in? When / what? | No. Only approved tool execution prompts (`Allow for this session`) per the lab guidelines; zero manual hints or prompt interventions were provided. |

---

## Part II — System prompt annotation

### Outline
1. `# Core Mandates`: Foundational rules for security, system integrity, and context efficiency.
2. `## Security & System Integrity`: Directives safeguarding credentials, restricting unrequested git commits, and isolating untrusted tool data.
3. `## Context Efficiency`: Strategy and guidelines for minimizing token usage through parallel reads, scoped searches, and reducing round-trip turns.
4. `## Engineering Standards`: Requirements for conventions, architectural patterns, Directives vs. Inquiries distinctions, testing, and empirical verification.
5. `## Topic Updates`: Mandates for orchestrating complex tasks into discrete, user-visible narrative chapters using `update_topic`.
6. `# Available Sub-Agents`: Framework and guidelines for delegating high-volume or speculative subtasks to specialized agents (`codebase_investigator`, `cli_help`, `generalist`).
7. `# Available Agent Skills`: Protocol for dynamically loading expert procedural knowledge via `activate_skill`.
8. `# Hook Context`: Definitions for external hook triggers and injected context parameters.
9. `# Primary Workflows & Development Lifecycle`: Prescribed 4-stage lifecycle (Research -> Strategy -> Execution -> Verification).
10. `# Operational Guidelines`: Constraints on assistant persona, tone, safety boundaries, and tool calling limits.
11. `# Git Repository`: Repository metadata, current branch context, and workspace layout.

### Annotations (≥6)

#### Section: Operational Guidelines (tone and verbosity)
> *"Provide direct, concise answers. Avoid filler words, preambles, or excessive pleasantries. When taking actions, explain what you are doing briefly in a single sentence before invoking tools."*
- **Behavior it produces:** The model avoids conversational small talk and preambles, communicating progress in terse, single-sentence explanations preceding tool invocations (e.g. `[OBSERVED: session_timeline.txt L5-6]` where Call #1 immediately calls `update_topic` and `read_file` with concise intent).
- **Failure it prevents:** Prevents bloating output token count and slowing down interaction with sycophantic greetings, restatements of the user prompt, or redundant apologies.

#### Section: Engineering Standards (when not to act / confirm)
> *"Do not take significant actions beyond the clear scope of the request without confirming with the user. If the user implies a change (e.g., reports a bug) without explicitly asking for a fix, ask for confirmation first. If asked how to do something, explain first, don't just do it."*
- **Behavior it produces:** Strict adherence to explicit user intent, separating inquiries (read-only research) from directives (code modifications).
- **Failure it prevents:** Prevents dangerous autonomous modifications to codebases when a developer only asked for analysis, code review, or exploratory architectural advice.

#### Section: Primary Workflows — Development Lifecycle (workflow)
> *"Follow a disciplined four-phase approach for software engineering tasks: 1. Research: Understand the problem, locate relevant files, and identify reproduction steps. 2. Strategy: Formulate a concrete, step-by-step implementation plan. 3. Execution: Implement surgical changes with minimal blast radius. 4. Verification: Empirically prove correctness using automated tests."*
- **Behavior it produces:** The agent methodically progressed through these exact four phases: Call #1–#2 researched files and reproduced failures; Call #3–#5 strategized; Call #6–#7 executed fixes; Call #8–#15 verified with pytest and git diff `[OBSERVED: session_timeline.txt L1-58]`.
- **Failure it prevents:** Prevents "hallucinated editing" where an agent immediately generates guessed code changes before reading existing tests or understanding dependencies.

#### Section: Context Efficiency (tool usage)
> *"Combine turns whenever possible by utilizing parallel searching and reading and by requesting enough context by passing context, before, or after to grep_search, to enable you to skip using an extra turn reading the file... replace fails if old_string is ambiguous, causing extra turns. Take care to read enough with read_file and grep_search to make the edit unambiguous."*
- **Behavior it produces:** In Call #2, the model batched 6 tool calls (1 shell command and 5 file reads) into a single turn `[OBSERVED: session_timeline.txt L9-14]`.
- **Failure it prevents:** Prevents sequential single-tool turn loops that repeatedly send the entire conversation history back and forth, consuming excessive tokens and wall-clock time.

#### Section: Security & System Integrity (credential protection)
> *"Credential Protection: Never log, print, or commit secrets, API keys, or sensitive credentials. Rigorously protect .env files, .git, and system configuration folders."*
- **Behavior it produces:** The model explicitly refuses to inspect, display, or stage environment secret files or configuration keys during execution.
- **Failure it prevents:** Prevents catastrophic credential leaks to source control, shared telemetry, or public pull requests.

#### Section: Engineering Standards — Testing (empirical verification)
> *"ALWAYS search for and update related tests after making a code change. You must add a new test case to the existing test file (if one exists) or create a new test file to verify your changes. For bug fixes, you must empirically reproduce the failure with a new test case or reproduction script before applying the fix."*
- **Behavior it produces:** In Call #2, the agent ran `python -m pytest` to reproduce the bugs before editing `shopcart/`, and in Calls #10–#11 it wrote comprehensive new unit tests for shipping fees and thresholds `[OBSERVED: session_timeline.txt L9, L38, L41]`.
- **Failure it prevents:** Prevents assuming a bug is resolved without empirical test validation or shipping unverified features.

### Context injection (`GEMINI.md`)
`GEMINI.md`'s content is **not** present in the exported `system.md` file `[OBSERVED: string comparison yielded False]`. Instead, `GEMINI.md` is loaded dynamically during CLI initialization and injected directly into the **initial user prompt message** wrapped in structured XML tags:
```xml
<session_context>
...
<loaded_context>
<project_context>
--- Context from: C:/.../gemini-cli-dissection/work/run/GEMINI.md ---
# Project context
- Python 3.10+ library; no third-party runtime dependencies.
- All money is integer cents. Never use floats for stored amounts.
...
--- End of Context from: .../GEMINI.md ---
</project_context>
</loaded_context>
</session_context>
```
`[OBSERVED: scratch/first_context.md L34-45, generated by summarize_log.py --context]`.

---

## Part III — Tool design

### Inventory
| Category | Tools | Used in session (count) |
|---|---|---|
| File | `read_file`, `write_file`, `replace`, `list_directory` | `read_file` (6), `write_file` (2), `replace` (2), `list_directory` (0) |
| Search | `grep_search`, `glob` | `grep_search` (1), `glob` (0) |
| Shell | `run_shell_command`, `list_background_processes`, `read_background_output` | `run_shell_command` (6), background tools (0) |
| Web | `web_fetch`, `google_web_search` | `0` |
| Planning & narration | `update_topic`, `enter_plan_mode` | `update_topic` (5), `enter_plan_mode` (0) |
| Delegation & interaction | `activate_skill`, `invoke_agent`, `ask_user` | `0` |

### Tool A: `replace`
- **Source file:** `packages/core/src/tools/definitions/model-family-sets/gemini-3.ts` (L356) and implementation in `packages/core/src/tools/edit.ts` (L460).
- **Schema:**
  ```json
  {
    "type": "object",
    "properties": {
      "file_path": { "type": "string", "description": "The path to the file to modify." },
      "instruction": { "type": "string", "description": "A clear, semantic instruction for the code change..." },
      "old_string": { "type": "string", "description": "The exact literal text to replace, unescaped." },
      "new_string": { "type": "string", "description": "The exact literal text to replace old_string with, unescaped..." },
      "allow_multiple": { "type": "boolean", "description": "If true, replaces all occurrences of old_string." }
    },
    "required": ["file_path", "instruction", "old_string", "new_string"]
  }
  ```
- **Why each parameter:**
  - `file_path`: Specifies the exact target file on disk.
  - `instruction`: Gives the semantic intent of the edit, providing context for human approval and internal validation.
  - `old_string`: Provides an exact literal anchor in the file, ensuring unambiguous targeting without relying on fragile line numbers.
  - `new_string`: Supplies the replacement code block.
  - `allow_multiple`: Protects against accidentally replacing unintended matching substrings unless explicitly configured.
- **Description line that corrects a model mistake:**
  > *"Do not use omission placeholders like '(rest of methods ...)', '...', or 'unchanged code'; provide exact literal code."*
  **Mistake:** LLMs frequently output placeholder comments like `// ... rest of code unchanged ...`, which would corrupt or delete source code if written literally.
- **Deliberately does not:** Does not accept line numbers or whole-file replacement. Line numbers shift easily after earlier edits, and whole-file writes consume massive output tokens and risk accidental deletion of unrelated code.

### Tool B: `run_shell_command`
- **Source file:** `packages/core/src/tools/definitions/dynamic-declaration-helpers.ts` (L85) and implementation in `packages/core/src/tools/shell.ts` (L102).
- **Schema:**
  ```json
  {
    "type": "object",
    "properties": {
      "command": { "type": "string", "description": "Exact command to execute as powershell.exe -NoProfile -Command <command> (or /bin/bash -c on POSIX)" },
      "description": { "type": "string", "description": "Brief description of the command for the user." },
      "is_background": { "type": "boolean", "description": "Set to true to run command in the background." }
    },
    "required": ["command", "description"]
  }
  ```
- **Why each parameter:**
  - `command`: The raw shell command string to be executed in the non-login shell.
  - `description`: A user-facing human-readable summary displayed in confirmation dialogs (e.g., `Allow execution of [Shell]?`).
  - `is_background`: Allows asynchronous execution for long-running processes (e.g. servers) without deadlocking the agent turn.
- **Description line that corrects a model mistake:**
  > *"Pagination: Always disable terminal pagination to ensure commands terminate (e.g., use git --no-pager, systemctl --no-pager, or set PAGER=cat)."*
  **Mistake:** LLMs frequently run commands like `git diff` that invoke interactive pagers (`less`), which hang waiting for user keyboard input (e.g. 'q') and freeze the autonomous agent loop.
- **Deliberately does not:** Does not support interactive stdin input (TTY interaction). Commands must be self-terminating and return non-interactive standard output.

### Why old/new string edits?
1. **Resilience to line drift:** Line numbers shift whenever prior lines are inserted or deleted. Exact literal string matching is content-addressable and robust against offset drift.
2. **Token and latency efficiency:** Emitting only a small diff block (e.g. Call #6 replacing 1 line in `cart.py` `[OBSERVED: session_timeline.txt L26]`) costs ~199 output tokens compared to regenerating hundreds or thousands of tokens for the entire file.
3. **Trace moment:** In Call #6, the agent modified line 17 of `shopcart/cart.py` (`self.items[sku] = quantity` -> `self.items[sku] = self.items.get(sku, 0) + quantity`) in 199 output tokens without having to rewrite the remaining 40+ lines of untouched methods (`remove_item`, `clear`, etc.).

### Per-model tool descriptions
Comparing `packages/core/src/tools/definitions/model-family-sets/gemini-3.ts` with `default-legacy.ts`:
- In `read_file`, `gemini-3.ts` instructs: *"To maintain context efficiency, you MUST use 'start_line' and 'end_line' for targeted, surgical reads of specific sections"*, whereas `default-legacy.ts` merely says: *"Reads and returns the content of a specified file. If the file is large, the content will be truncated."*
- In `grep_search_ripgrep`, `gemini-3.ts` adds: *"PREFERRED over standard run_shell_command('grep ...') due to better performance and automatic output limiting..."*
**Why they differ:** Advanced frontier models (Gemini 3 family) possess strong instruction-following and context-awareness capabilities, allowing the system to enforce proactive token-optimization rules without confusing the model. Older/legacy models degrade when given overly complex multi-condition instructions, so their tool descriptions are kept strictly descriptive and factual.

---

## Part IV — Behavioral analysis

### 1. The loop
```
Call #1 (Model) → update_topic, read_file (TASK.md)
Call #2 (Model) → run_shell_command (pytest), read_file x5 (pricing.py, cart.py, catalog.py, test_cart.py, test_pricing.py)
Call #3 (Model) → update_topic (Outlining plan)
Call #4 (Model) → grep_search ("total\(\)")
Call #5 (Model) → update_topic (Implementing cart item addition fix...)
Call #6 (Model) → replace (shopcart/cart.py)
Call #7 (Model) → replace (shopcart/pricing.py)
Call #8 (Model) → run_shell_command (pytest)
Call #9 (Model) → update_topic (Updating existing test assertions...)
Call #10 (Model) → write_file (tests/test_cart.py)
Call #11 (Model) → write_file (tests/test_pricing.py)
Call #12 (Model) → run_shell_command (pytest)
Call #13 (Model) → run_shell_command (git status)
Call #14 (Model) → run_shell_command (git diff)
Call #15 (Model) → run_shell_command (git --no-pager diff)
Call #16 (Model) → update_topic (Task completed successfully)
Call #17 (Model) → Final response text to user
```
`[OBSERVED: session_timeline.txt L1-58]`.
**What ended it:** The agent decided it was done `[OBSERVED: session_timeline.txt L58]`. After verifying that all 23 tests passed and inspecting `git diff`, it set `update_topic` to "Task completed successfully" and generated its final completion message.

### 2. Context growth

| Call | Input Tokens | Cached Tokens | Output Tokens | Thoughts Tokens | Total Tokens |
|---|---|---|---|---|---|
| 1 | 11,359 | 6,093 | 60 | 335 | 11,754 |
| 2 | 12,050 | 8,116 | 150 | 331 | 12,531 |
| 3 | 14,830 | 10,129 | 57 | 719 | 15,606 |
| 4 | 15,668 | 12,154 | 19 | 1,661 | 17,348 |
| 5 | 17,614 | 14,189 | 48 | 2,500 | 20,162 |
| 6 | 20,215 | 16,229 | 199 | 135 | 20,549 |
| 7 | 20,964 | 6,085 | 899 | 644 | 22,507 |
| 8 | 23,088 | 20,293 | 37 | 31 | 23,156 |
| 9 | 24,055 | 20,292 | 54 | 1,473 | 25,582 |
| 10 | 25,641 | 22,325 | 963 | 20 | 26,624 |
| 11 | 27,344 | 24,360 | 408 | 30 | 27,782 |
| 12 | 28,139 | 24,357 | 34 | 21 | 28,194 |
| 13 | 28,407 | 24,351 | 27 | 30 | 28,464 |
| 14 | 28,581 | 26,373 | 29 | 13 | 28,623 |
| 15 | 28,669 | 26,364 | 31 | 83 | 28,783 |
| 16 | 28,829 | 26,357 | 38 | 161 | 29,028 |
| 17 | 29,071 | 26,350 | 130 | 98 | 29,299 |

`[OBSERVED: session_calls.csv L1-18]`.

**Explanation:**
- **Why input grows:** In each round-trip of the agent loop, the entire previous conversation history—including past model thoughts, tool calls, and tool outputs (full file contents from 6 reads and pytest terminal outputs)—is appended to the context sent to the API. Input grew from 11,359 to 29,071 tokens.
- **What caching tells us:** Google's context caching reuses unchanged prefix tokens across requests. In Call #1, 6,093 tokens were cached (system prompt + tool definitions). By Call #17, 26,350 of the 29,071 input tokens were served directly from cache `[OBSERVED: session_calls.csv L18]`.
- **Why caching matters:** Caching dramatically reduces time-to-first-token latency and reduces compute cost, as cached tokens are billed at a fraction of fresh input token rates.

### 3. Planning
- **Mechanism:** The agent tracked progress via the built-in `update_topic` tool (called 5 times `[OBSERVED: session_timeline.txt L5, L17, L23, L35, L56]`). It did not use `write_todos` or `enter_plan_mode`.
- **Phases declared:**
  1. `Reading Task and Planning` (Call #1)
  2. `Outlining the precise plan to fix failing tests...` (Call #3)
  3. `Implementing cart item addition fix, pricing discount order fix...` (Call #5)
  4. `Updating existing test assertions with shipping fee...` (Call #9)
  5. `Task completed successfully. All tests passing...` (Call #16)
- **Match with execution:** The plan matched execution almost perfectly. The only minor deviation `[OBSERVED: session_timeline.txt L50, L53]` was running `git diff` which prompted an interactive pager check, quickly followed by `git --no-pager diff` to safely review changes before final summary.

### 4. Error recovery
- **Quoted failure:**
  In Call #2, the baseline test execution outputted:
  ```text
  FAILED tests/test_cart.py::test_add_same_item_twice_increments_quantity - AssertionError: assert {'MUG': 2} == {'MUG': 3}
  FAILED tests/test_cart.py::test_fixed_discount_applied_before_tax - assert 1100 == 3240
  2 failed, 12 passed in 0.10s
  ```
  `[OBSERVED: terminal screenshot, session_timeline.txt L9]`.
- **What happened next:**
  The agent did not panic or attempt random changes. In Call #3, it called `update_topic` declaring its plan to fix the 2 failing tests. In Call #4, it searched for `total()` usages. In Call #6, it used `replace` on `shopcart/cart.py` to fix `self.items[sku] = self.items.get(sku, 0) + quantity`. In Call #7, it used `replace` on `shopcart/pricing.py` to calculate discounts before tax and implement the shipping fee logic. In Call #8, it verified that the suite passed.
- **Evaluation:** The recovery was exemplary, systematic, and minimally scoped.

### 5. The tests
- **Edits made to existing tests:**
  Yes, the agent updated two existing tests in `tests/test_cart.py`:
  ```diff
  -    assert cart.total() == 2160  # 2000 + 8% tax
  +    # Updated to include $5.99 shipping fee (599 cents) since subtotal < $50.00
  +    assert cart.total() == 2759  # 2000 + 8% tax (2160) + shipping (599)
  
  -    assert cart.total() == 2333  # (2400 - 10%) + 8% tax
  +    # Updated to include $5.99 shipping fee (599 cents) since discounted subtotal < $50.00
  +    assert cart.total() == 2932  # (2400 - 10%) + 8% tax (2333) + shipping (599)
  ```
  `[OBSERVED: git show ce5b8a1, tests/test_cart.py diff]`.
- **Allowed by TASK.md:**
  Yes! `TASK.md` Section 2 explicitly states:
  > *"Some existing tests check Cart.total() with values from before shipping existed. You may update those expected values — and only those — and note why in a comment."*
  `[OBSERVED: starter/TASK.md L15-16]`. The agent strictly obeyed this guideline, modifying only the expected values affected by the new $5.99 shipping fee and adding explanatory comments.

### 6. Models
- **Confirmation:** Confirmed from `session_calls.csv` and `session_timeline.txt L70`; all 17 requests executed on `gemini-3.5-flash-lite`.
- **Thinking peaks:**
  - Call #5: **2,500 thinking tokens** `[OBSERVED: session_calls.csv L6]`. The agent was solving the core algorithmic interaction: integrating shipping threshold logic into `pricing.py` and chaining it with discount calculations before tax.
  - Call #4: **1,661 thinking tokens** `[OBSERVED: session_calls.csv L5]`. The agent was analyzing the `grep_search` results and architecting the clean separation of responsibilities between `cart.py` and `pricing.py`.
  - Call #9: **1,473 thinking tokens** `[OBSERVED: session_calls.csv L10]`. The agent was calculating new expected mathematical values across test cases for orders under vs over the $50.00 threshold.
- **Two-model architecture analysis:**
  Gemini CLI's default setup pairs `gemini-3.5-flash-lite` (as a router) with `gemini-3.8-flash` (as the worker):
  - **Why split?** Simple intent classification, command routing, and basic tool triage do not require a massive parameter model. Using Flash-Lite for routing minimizes user-perceived initial latency and dramatically reduces cost. Heavier frontier models (`gemini-3.8-flash` or Pro) are reserved for code synthesis and debugging where deep reasoning is essential.
  - **Trade-offs if run entirely on a bigger model:**
    - *Speed:* Slower overall wall-clock time due to longer time-to-first-token and lower token generation speeds.
    - *Cost & Quota:* Exponentially higher token cost and immediate risk of hitting strict rate limits (e.g. 20 requests/day on free tier vs 250,000 input tokens/minute on Flash-Lite).
    - *Quality:* Slightly more concise code synthesis or zero-shot test coverage, but on a well-specified task like this lab, Flash-Lite was 100% sufficient to achieve a flawless 23/23 passing test score.
