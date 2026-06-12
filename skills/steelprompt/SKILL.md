---
name: steelprompt
description: Use to manually engineer any prompt before sending it. Applies all 7 official Anthropic prompt engineering principles and rewrites a complete, structured version. Also supports switching modes.
---

# steelprompt

Apply Anthropic's official prompt engineering guidelines to any prompt.

## Usage

```
/steelprompt "your prompt to improve"
/steelprompt mode full|preview|ask-only|off
```

---

## Mode switching

If the received prompt matches `/steelprompt mode X`:

1. Run `Bash(echo $CLAUDE_PLUGIN_ROOT)` to get the plugin root path, then write `{"mode": "X"}` to `<CLAUDE_PLUGIN_ROOT>/.steelpromptrc` using the Write tool with the absolute path
2. Confirm: "Mode changed to **X**. Active from the next prompt."

Available modes:
| Mode | Automatic hook behavior |
|---|---|
| `full` | Applies 3-tier framework silently (default) |
| `preview` | Same logic as `full`, shows the engineered prompt before executing |
| `ask-only` | Asks only if critical information is missing; does not apply the full framework |
| `off` | Hook completely disabled |

---

## Manual prompt rewriting

### If the prompt is vague
(critical context is missing that would significantly change the result)

Use `AskUserQuestion` with 1–2 concrete questions. Do not proceed further.

Threshold: file unspecified = vague; output type unspecified = vague; "fix" without context = vague.

### Chain detection

Before rewriting: does the task explicitly combine two or more sequential operations, connected by "then", "and then", "+", "after", or a comma joining separate actions?
Operations: refactor, test, document, deploy, migrate, review, implement, verify, analyze, fix, write, run

Examples that trigger chain detection: "refactor then test", "implement and document", "analyze + fix + deploy"
Examples that do NOT trigger: "refactor this function", "test the login flow", "document the API"

If yes — do NOT rewrite as a single prompt. Show a chain plan:

  Chain detected (N prompts):
  -> Prompt 1: [task A — produces: output description]
  -> Prompt 2: [task B — uses: output of Prompt 1]
  -> ... (one prompt per operation)
  -> Prompt N: [final task — uses: all prior outputs]

Then use AskUserQuestion:
- "Run in sequence" — execute Prompt 1 now; user pastes output for next
- "Run as single prompt" — merge into one structured prompt and execute
- "Cancel" — stop

### If the prompt is clear or complex

Apply all applicable Anthropic principles:

**Principles to apply (all, if relevant):**

1. **Role** — `You are a [precise role based on task domain]`
2. **Context** (`<context>`) — all relevant context BEFORE the task: files, project, environment, known constraints from the conversation. If the task references long files or documents, embed them inside `<context>` BEFORE the task description — never after.
3. **Task** (`<task>`) — imperative mood ("Analyze", "Implement", "Fix"); numbered steps if multi-step
4. **Constraints** (`<constraints>`) — what NOT to do, edge cases, limits, style requirements. If the task involves irreversible operations (delete, drop, rm, mv to overwrite, remove, overwrite, truncate, push --force, git reset --hard, destroy, wipe, DROP TABLE, DELETE FROM, ALTER TABLE...DROP), automatically add: (a) explicit confirmation before each destructive action; (b) minimal scope — only touch what is explicitly mentioned; (c) intermediate checkpoints for long operations.
5. **Output format** (`<output_format>`) — exact structure: type (code/list/prose), length, sections, format. If the format is rigidly critical (JSON, YAML, SQL), add a prefill note: begin the response with the opening character of that format ({, ---, SELECT).
6. **Chain of thought** — `Think through this step by step before answering` for complex or multi-step tasks
7. **Examples** (`<examples>`) — 2–3 `<example>Input: ... Output: ...</example>` if the task is ambiguous or the output format is non-obvious, ONLY if inferable from existing context (conversation, codebase). For ambiguous tasks or where format precision matters, add one `<bad_example>` alongside each `<example>` — show what NOT to produce.

**Base template:**

```
You are a [precise role].

<context>
[all relevant context: files, project, environment, known constraints]
</context>

<task>
[task in imperative mood, numbered steps if multi-step]
1. ...
2. ...
</task>

<constraints>
[what NOT to do, edge cases, limits]
</constraints>

<output_format>
[exact expected structure: type, length, sections, format]
</output_format>

<examples>
<example>
Input: ...
Output: ...
</example>
</examples>

Think through this step by step before answering.
```

Omit inapplicable sections. Do not fill with placeholders.

### Special cases

- Already XML-structured prompt → refine without dismantling the existing structure
- Atomic prompt → warn: "This prompt is already atomic and self-contained. No engineering needed." — stop here, do not show AskUserQuestion.
- Already well-structured prompt → note what is already good, suggest only real improvements

---

## Output format

Everything in the same message, no intermediate text:

1. Show the engineered prompt in a code block, preceded by `**Engineered prompt:**`
2. One line of explanation ONLY if a choice is non-obvious
3. Use `AskUserQuestion` with these options:
   - **"Run"** — execute the improved prompt immediately
   - **"Edit"** — show raw text without code block, say "Copy, edit, and paste as a new message."
   - **"Cancel"** — stop
