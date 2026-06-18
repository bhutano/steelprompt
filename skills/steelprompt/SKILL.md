---
name: steelprompt
description: Use to manually engineer any prompt before sending it. Applies all official Anthropic prompt engineering principles and rewrites a complete, structured version. Also supports switching modes.
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

Ask ONLY if:
1. The answer would fundamentally change the prompt (not just refine it)
2. It cannot be inferred from the prompt or conversation context
3. One simple, plain-language question is enough

If in doubt — infer and proceed. The skill does the work; the user should not need to understand prompt engineering.

Threshold: "fix" with no file or error = ask. "fix the login bug" with error in context = infer, proceed.

Ask with a single plain sentence. No jargon, no options lists, no parenthetical explanations.

Good: `"Which file are you working on?"` / `"What should the result look like?"` / `"Any specific library to use?"`
Bad: `"What output format do you prefer? (code, list, explanation, JSON)"` — technical, asks user to make a PE decision

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

Apply all applicable Anthropic principles below.

---

## Core principles (apply to all prompts)

### 1. Role
Assign a precise role based on task domain.

```
You are a senior [domain] engineer specializing in [specific area].
```

Skip for conversational or trivial tasks.

---

### 2. Context + Motivation
Place ALL relevant context BEFORE the task — files, project, environment, constraints.

**Key rule:** Explain the WHY behind the request, not just the WHAT. Claude generalizes from explanations.

- Bad: `NEVER use ellipses`
- Good: `Never use ellipses — the text-to-speech engine won't know how to pronounce them`

If the task references long documents, embed them in `<context>` tags BEFORE the task description — never after.

For multi-document tasks:
```xml
<documents>
  <document index="1">
    <source>filename.pdf</source>
    <document_content>{{CONTENT}}</document_content>
  </document>
</documents>
```

**Long context tip:** Place long data at the TOP of the prompt, above instructions and examples. Ask Claude to quote relevant passages before answering (improves accuracy by up to 30%).

---

### 3. Task
Write in imperative mood. Use numbered steps when order matters. Be explicit about whether Claude should act or suggest.

```xml
<task>
1. Analyze the authentication flow in auth.ts
2. Identify the three most likely sources of the token expiry bug
3. Implement the fix for the most likely cause
</task>
```

**Action vs. suggestion:**
- "Can you suggest changes?" → Claude suggests only
- "Change this function." / "Implement X." → Claude acts
- When intent is ambiguous, add: `By default, implement changes rather than only suggesting them.`

---

### 4. XML Structure
Wrap each section in its own descriptive XML tag. This reduces misinterpretation in complex prompts.

Standard tags: `<context>`, `<task>`, `<constraints>`, `<output_format>`, `<examples>`
For content: `<instructions>`, `<input>`, `<document>`, `<code>`

Use consistent tag names. Nest when hierarchy exists. Match tag names to content type.

---

### 5. Constraints
State what NOT to do, edge cases, limits, style requirements.

```xml
<constraints>
- Do not modify functions outside the auth module
- Match existing code style (no type annotations on internal helpers)
- Do not add error handling for scenarios the framework already handles
</constraints>
```

**Destructive operations** (delete, drop, rm, truncate, force push, reset --hard, ALTER TABLE...DROP, etc.) — automatically add:
- Explicit confirmation before each destructive action
- Minimal scope: only touch what is explicitly mentioned
- Intermediate checkpoints for long operations

**Anti-overeagerness** (add when scope creep is a risk):
```
Only make changes directly requested. Don't add features, refactor, or introduce abstractions
beyond what the task requires. Don't design for hypothetical future requirements.
Don't add error handling for scenarios that can't happen.
```

**Anti-hallucination** (add for code tasks):
```
Never speculate about code you have not read. Read the file before making claims.
Only state facts you can point to evidence for.
```

---

### 6. Output format
Specify exact structure: type (code/list/prose), length, sections, format.

Tell Claude what TO do — not what NOT to do:
- Bad: `Do not use markdown`
- Good: `Write in plain prose paragraphs. No bullet points or headers.`

Use XML format indicators:
```
Write the analysis in <findings> tags. Write recommendations in <recommendations> tags.
```

**For JSON/YAML/SQL:** Add prefill note — `Begin your response with the opening character of that format ({ or --- or SELECT)`.

**Verbosity control:**
- Shorter: `Provide concise responses. Skip non-essential context. One paragraph max.`
- Longer: `Include full reasoning, edge cases, and implementation notes.`

**LaTeX** (when plain text is needed):
```
Format in plain text only. Do not use LaTeX, MathJax, or markup notation.
Write math with standard text characters (/, *, ^).
```

**No prefill** (Claude 4.6+ deprecated prefilled assistant messages):
```
Respond directly without preamble. Do not start with 'Here is...', 'Based on...', etc.
```

---

### 7. Thinking
Add CoT for complex or multi-step tasks. Use thinking API for agentic workloads.

**Standard CoT:**
```
Think through this step by step before answering.
```

**Structured CoT** (separate reasoning from output):
```
Reason through the problem in <thinking> tags. Then provide your final answer in <answer> tags.
```

**Self-check:**
```
Before finishing, verify your answer against [test criteria / the requirements above].
```

**Thinking in examples:** Include `<thinking>` blocks in few-shot examples to show reasoning pattern. Claude generalizes the style.

**Adaptive thinking** (Claude 4.6+, API-level): Use `thinking: {type: "adaptive"}` + `effort` parameter instead of `budget_tokens`.
Effort levels: `low` → `medium` → `high` → `xhigh` → `max`
Default for most tasks: `high`. Coding/agentic: `xhigh`.

**Overthinking prevention** (when applicable):
```
Choose an approach and commit to it. Avoid revisiting decisions unless new information
directly contradicts your reasoning.
```

---

### 8. Examples
Add 2–3 examples ONLY if:
- Task is ambiguous or output format is non-obvious
- Examples are inferable from conversation or codebase

```xml
<examples>
<example>
Input: [example input]
Output: [expected output]
</example>
<bad_example>
Input: [same input]
Output: [what NOT to produce — wrong format, wrong scope, wrong tone]
</bad_example>
</examples>
```

For format-critical tasks, include `<bad_example>`. 3–5 examples for best results. Make them diverse (cover edge cases).

---

## Special cases

- Already XML-structured prompt → refine without dismantling the existing structure
- Atomic prompt → warn: "This prompt is already atomic and self-contained. No engineering needed." — stop here.
- Already well-structured prompt → note what is already good, suggest only real improvements

---

## Tool use prompts

When the prompt is for an agent or system that uses tools, add:

**Explicit action default:**
```
<default_to_action>
By default, implement changes rather than only suggesting them.
Use tools to discover missing details instead of guessing.
</default_to_action>
```

Or conservative:
```
<do_not_act_before_instructions>
Do not implement or change files unless explicitly instructed.
When intent is ambiguous, provide information and recommendations rather than taking action.
</do_not_act_before_instructions>
```

**Parallel tool calling:**
```
<use_parallel_tool_calls>
If you intend to call multiple tools with no dependencies between them,
make all calls in parallel. Maximize parallel tool use for speed and efficiency.
Never use placeholders or guess missing parameters.
</use_parallel_tool_calls>
```

---

## Agentic system prompts

When writing a system prompt for an autonomous agent, add relevant blocks:

**Autonomy and safety:**
```
Take local, reversible actions freely (edit files, run tests).
For destructive or hard-to-reverse actions (delete, force push, drop tables, post externally),
confirm with the user before proceeding.
```

**Long-horizon / multi-window:**
```
Your context window will be automatically compacted. Do not stop tasks early due to token budget
concerns. Save progress and state to memory before context refreshes.
```

**Progress reporting:**
```
Before reporting progress, audit each claim against a tool result from this session.
Only report work you can point to evidence for. If something is not verified, say so explicitly.
```

**Subagent orchestration:**
```
Use subagents when tasks can run in parallel, require isolated context, or involve independent
workstreams. For simple tasks, sequential operations, or single-file edits, work directly.
```

**State management:** Use JSON for structured state (test results, task status). Use freeform text for progress notes. Use git for checkpoints.

---

## Model-specific notes

### Claude Fable 5 / Mythos 5
- Safety classifiers cover offensive cybersecurity + biology — configure fallback to Opus 4.8
- Default `effort: high`; use `xhigh` for most capability-sensitive work
- Strong instruction following: brief instructions work, no need to enumerate behaviors
- Tends to overplan on ambiguous tasks — add brevity/action instruction
- More likely to take unrequested actions — define explicit boundaries
- Dispatches parallel subagents more readily
- Performs well with memory systems (lesson files)
- Don't instruct to echo reasoning in response text (triggers `reasoning_extraction` refusal)
- Give reason + request: `I'm working on [X] for [Y]. They need [Z]. With that in mind: [request].`
- For async autonomous runs: add no-ask instruction + send_to_user tool

### Claude Opus 4.8
- Thinking off by default — set `thinking: {type: "adaptive"}` to enable
- `xhigh` effort: best for coding/agentic; start with 64k max_tokens
- Literal instruction following — state scope explicitly, don't rely on generalization
- Tends to favor reasoning over tools — raise effort or instruct explicitly to use specific tools
- Default frontend style: cream/serif/terracotta — specify concrete alternative or ask model to propose options
- Code review: by default filters findings to stated bar — instruct for coverage, not filtering, if recall matters
- Spawns fewer subagents — explicitly guide when delegation is appropriate

---

## Base template

```
You are a [precise role].

<context>
[all relevant context: files, project, environment, constraints]
[motivation: why this matters / what outcome it enables]
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

---

## Output format

Everything in the same message, no intermediate text:

1. Show the engineered prompt in a code block, preceded by `**Engineered prompt:**`
2. One line of explanation ONLY if a choice is non-obvious
3. Use `AskUserQuestion` with these options:
   - **"Run"** — execute the improved prompt immediately
   - **"Edit"** — show raw text without code block, say "Copy, edit, and paste as a new message."
   - **"Cancel"** — stop
