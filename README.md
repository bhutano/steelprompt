<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <img src="assets/banner-light.svg" alt="steelprompt" width="100%">
</picture>

<div align="center">

🌐 **English** · [中文](docs/README.zh.md) · [Español](docs/README.es.md) · [PT-BR](docs/README.pt-BR.md) · [日本語](docs/README.ja.md) · [한국어](docs/README.ko.md) · [Deutsch](docs/README.de.md) · [Français](docs/README.fr.md) · [Italiano](docs/README.it.md)

[![Version](https://img.shields.io/badge/version-0.3.1-4a9eff?style=flat-square)](https://github.com/bhutano/steelprompt/releases/tag/v0.3.1)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](https://github.com/bhutano/steelprompt/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-f59e0b?style=flat-square)](https://python.org)
[![Claude Code](https://img.shields.io/badge/claude_code-2.0.22+-a78bfa?style=flat-square)](https://claude.ai/code)

![demo](steel_demo.gif)

**Every prompt restructured using Anthropic's 10 official principles — automatically in Claude Code, on demand in Claude.ai.**

✦ No API keys · ✦ Claude Code + Claude.ai web · ✦ Zero added latency · ✦ 4 switchable modes

</div>

---

## The problem

Claude is only as good as the prompts you give it. Most prompts are missing role assignment, structured context, explicit constraints, output format specification, and examples — all things Anthropic's own guidelines say dramatically improve response quality.

You could spend 10 minutes engineering every prompt manually. Or use steelprompt — automatic in Claude Code, on demand in Claude.ai.

---

## How it works

steelprompt runs on two surfaces:

- **Claude Code (CLI)** — a `UserPromptSubmit` hook intercepts every prompt automatically before Claude processes it.
- **Claude.ai (web)** — paste `prompts/steelprompt-web.md` into Custom Instructions once, then use `/sp "prompt"` to engineer any prompt on demand.

In both cases, the same 3-tier decision protocol applies:

```
Your prompt
    │
    ▼
┌─────────────────────────────────────────────────┐
│  TIER 1 — BYPASS                                │
│  Slash commands · < 5 words · atomic tasks      │
│  → Pass through unchanged                       │
└─────────────────────────────────────────────────┘
    │ not bypassed
    ▼
┌─────────────────────────────────────────────────┐
│  TIER 2 — ASK                                   │
│  Critical information missing?                  │
│  → AskUserQuestion (1–2 targeted questions)     │
└─────────────────────────────────────────────────┘
    │ prompt is clear
    ▼
┌─────────────────────────────────────────────────┐
│  TIER 3 — APPLY FRAMEWORK           ← default   │
│  Restructure using 10 Anthropic principles      │
│  silently, before Claude responds               │
└─────────────────────────────────────────────────┘
```

No external API calls. Claude restructures inline during its normal inference — zero added latency, zero extra tokens billed.

---

## Demo

![steelprompt demo](assets/demo.gif)

---

## Tier 3 in action

This is the core of steelprompt. Every clear, non-atomic prompt goes through it automatically.

**You type:**
```
add rate limiting to the auth endpoints
```

**What steelprompt injects internally** (visible in `preview` mode before execution):
```
You are a senior backend security engineer.

<context>
Project: Express.js API with JWT authentication
Endpoints affected: POST /auth/login, POST /auth/refresh, POST /auth/register
Environment: Node.js 20, existing middleware stack in src/middleware/
Known constraints from conversation: Redis already in use for session storage
</context>

<task>
Implement rate limiting on authentication endpoints:
1. Add per-IP rate limiting: max 5 requests/minute on /login and /register
2. Add per-user rate limiting: max 20 requests/hour on /refresh
3. Return 429 with Retry-After header on limit exceeded
4. Do not affect non-auth endpoints
</task>

<constraints>
- Reuse existing Redis connection, do not introduce a new client
- Do not modify JWT validation logic
- Rate limit state must survive server restarts
- Follow existing middleware patterns in src/middleware/
</constraints>

<output_format>
1. New middleware file with implementation
2. Diff showing changes to auth routes
3. Two Jest test cases: limit hit + normal flow
</output_format>

Think through this step by step before answering.
```

**What Claude produces:** a complete, production-ready implementation with tests — not a generic overview of rate limiting options.

---

## Advanced Patterns

steelprompt extends the core framework with context-specific patterns from the full Anthropic documentation — applied automatically when the prompt signals them:

### Chain detection

When a task spans multiple sequential operations, steelprompt detects the chain and shows a plan before executing.

**You type:**
```
refactor auth.py, add tests, update the documentation
```

**steelprompt detects a multi-step chain and pauses for confirmation:**
```
Chain detected (3 prompts):
→ Prompt 1: Refactor auth.py following SOLID principles
             Produces: refactored auth.py
→ Prompt 2: Write pytest tests for the refactored code
             Uses: output of Prompt 1
→ Prompt 3: Update docs/auth.md
             Uses: output of Prompt 1 + 2
```

Then asks: **Run in sequence · Run as single prompt · Cancel**

---

### Agentic safety

When a task involves irreversible operations, steelprompt automatically injects safety constraints.

**You type:**
```
delete all obsolete records from the production database
```

**steelprompt automatically adds to `<constraints>`:**
```
- Show COUNT of affected rows before executing DELETE
- Scope: only rows matching the explicit filter condition
- Require explicit confirmation before the irreversible action
- Do not touch tables or columns not explicitly mentioned
```

---

### Prefill for critical formats

When the output format is rigidly critical (JSON, YAML, SQL), steelprompt adds a prefill anchor: begin the response with the opening character (`{`, `---`, `SELECT`) to lock Claude into the correct format from the first token.

```
You type: "parse this config and return JSON"
steelprompt adds to <output_format>: begin response with {
```

---

### Negative examples

For ambiguous tasks where the correct output format is non-obvious, steelprompt generates `<bad_example>` blocks alongside `<example>` blocks — showing what **not** to produce reduces hallucinations on format-sensitive tasks.

```
<example>
Input: user object → Output: {id, name, email} (no password field)
</example>
<bad_example>
Input: user object → Output: {id, name, email, password_hash} ← never expose this
</bad_example>
```

---

### Motivation / WHY

Claude generalizes from explanations — steelprompt adds the reason behind a request, not just the request itself. A constraint with a WHY sticks better than a bare rule.

| Without steelprompt | With steelprompt |
|---|---|
| `NEVER use ellipses` | `Never use ellipses — the text-to-speech engine can't pronounce them` |
| `Keep responses short` | `Keep responses under 3 sentences — output is rendered in a mobile tooltip with limited space` |

---

### Format control (positive framing)

When an output format is specified, steelprompt tells Claude what TO produce — not what to avoid. Positive instructions are more reliable than negative ones.

```
You type: "answer in plain text, no markdown"
steelprompt adds to <output_format>: Write in smoothly flowing prose paragraphs.
                                     No headers, bullets, or code blocks.
```

For preamble-free output:
```
steelprompt adds: Respond directly without preamble.
                  Do not start with 'Here is...', 'Based on...', etc.
```

---

### Tool use & parallel calling

When a prompt is for an agent or system with tools, steelprompt injects parallel execution and action-default guidance.

**You type:**
```
build an agent that searches our docs, reads the top 3 results, and summarizes them
```

**steelprompt adds to `<constraints>`:**
```
Make all independent tool calls in parallel — search + read all 3 results simultaneously.
Never use placeholders or guess missing parameters.
By default, implement changes rather than only suggesting them.
```

---

### Thinking & self-check

For tasks that require multi-step reasoning or verification, steelprompt adds structured thinking and a self-check instruction.

```
You type: "calculate the optimal batch size for our embedding pipeline"

steelprompt adds:
  Reason through the problem in <thinking> tags.
  Consider: throughput, memory, API rate limits, cost per token.
  Then provide your answer in <answer> tags.
  Before finishing, verify your recommendation satisfies all constraints above.
```

---

### Long context ordering

When the task references long files or documents, steelprompt moves them **before** the task description inside `<context>` — matching Anthropic's guideline that long data should precede the query (up to 30% accuracy gain on complex inputs).

```
steelprompt also adds: Quote the relevant sections before answering.
```

| Without steelprompt | With steelprompt |
|---|---|
| `<task>` first, then file content | file content inside `<context>` first, then `<task>` |
| Query before evidence | Evidence before query |

---

## Tier 2 in action

When critical information is missing, steelprompt asks before guessing.

| You type | steelprompt asks |
|---|---|
| `"improve the code"` | Which file? What kind of improvement — readability, performance, correctness? |
| `"fix the bug"` | Which bug? Any reproduction steps or error message? |
| `"refactor auth"` | What's the goal? Is this API-public or internal? Should behavior stay identical? |
| `"change icon color to red"` | *(Tier 1 — atomic, direct response)* |

---

## Modes

| Mode | Behavior |
|---|---|
| `full` (default) | 3-tier protocol active: bypass → ask → apply 10 Anthropic principles |
| `preview` | Shows the engineered prompt before executing — review, edit, or cancel |
| `ask-only` | Asks clarifying questions only; does not apply the full framework |
| `off` | Hook completely disabled |

```bash
/steelprompt mode full
/steelprompt mode preview
/steelprompt mode ask-only
/steelprompt mode off
```

Config stored per-user in `$CLAUDE_PLUGIN_ROOT/.steelpromptrc`. Zero config = defaults to `full`.

---

## Preview mode

Want to see the engineered prompt before it runs? Switch to `preview`:

```
/steelprompt mode preview
```

Then type any prompt normally. Instead of responding silently, Claude will show you the restructured prompt and ask: **Run · Edit · Cancel**.

If you write in a language other than English, the preview is shown translated into your language — but **Run** always executes the English version, which Claude processes more accurately.

---

## Manual skill: `/steelprompt`

Use it to manually engineer any prompt — or to switch modes.

```
/steelprompt "migrate the users table to add soft deletes"
```

**Output:**
```
You are a senior database engineer specializing in PostgreSQL migrations.

<context>
Project: Rails 7 application with PostgreSQL
Table: users (id, email, created_at, updated_at)
Migration system: ActiveRecord
Known constraints: zero-downtime deployment required, table has ~2M rows
</context>

<task>
Add soft delete support to the users table:
1. Add deleted_at timestamp column (nullable, default null)
2. Add index on deleted_at for query performance
3. Update User model with default_scope excluding deleted records
4. Add User#soft_delete and User#restore methods
</task>

<examples>
<example>
Input: User.destroy(42)
Output (after): sets deleted_at = now(), does not DELETE the row
</example>
<example>
Input: User.all
Output (after): returns only records where deleted_at IS NULL
</example>
</examples>

<constraints>
- Do not use a gem (acts_as_paranoid, discard) — implement directly
- Migration must be reversible (down method required)
- Do not alter existing indexes or foreign keys
- Keep existing hard-delete path available via User.unscoped.destroy
</constraints>

<output_format>
1. Migration file with up/down
2. Model changes (3–5 lines max)
3. Two unit tests: soft delete sets column, default scope excludes deleted
</output_format>

Think through this step by step before answering.
```

---

## Install

```bash
claude plugin marketplace add bhutano/bhutano-marketplace
claude plugin install steelprompt
```

**Requirements:** Claude Code 2.0.22+ · Python 3.8+

```bash
claude --version   # check Claude Code version
python --version   # check Python version
```

---

## Use on Claude.ai (web)

Don't use Claude Code? You can get the same prompt engineering framework directly on [claude.ai](https://claude.ai) — no install, no CLI.

**Setup (one time):**
1. Open [claude.ai](https://claude.ai) in your browser
2. Click your profile icon → **Settings** → **Profile**
3. Find **"Custom instructions"** (or *"How would you like Claude to respond?"*)
4. Open [`prompts/steelprompt-web.md`](https://raw.githubusercontent.com/bhutano/steelprompt/master/prompts/steelprompt-web.md) (raw text), select all → copy → paste it there → Save

That's it. Every prompt you write in Claude.ai will be silently restructured using the same 3-tier protocol before Claude responds.

**Manual trigger:** `/sp "your prompt"` · **Preview mode:** `/sp mode preview`

> The web version has no hooks or tool calls — it runs as a system prompt inside Claude.ai's native custom instructions.

---

## Bypass

steelprompt never intercepts these:

| Prefix | Behavior |
|---|---|
| `/command` | Slash commands pass through unchanged |
| `* prompt` | Explicit bypass — skip this prompt |
| `# prompt` | Explicit bypass — skip this prompt |
| < 5 words | Treated as atomic — direct response |

---

## The 10 Anthropic principles

steelprompt applies these to every non-bypassed, clear prompt:

| # | Principle | Applied as |
|---|---|---|
| 1 | **Role** | `You are a senior [domain] engineer...` |
| 2 | **Context + Motivation** | `<context>` — all relevant background before the task, including the WHY behind the request; long files/docs placed **before** the task description |
| 3 | **Task** | `<task>` — imperative mood, numbered steps; explicit about action vs. suggestion |
| 4 | **XML Structure** | Every section wrapped in descriptive tags (`<context>`, `<task>`, `<constraints>`, `<output_format>`, `<examples>`) for unambiguous parsing |
| 5 | **Constraints** | `<constraints>` — what NOT to do, limits, style rules; agentic safety constraints auto-injected for destructive ops; anti-overeagerness and anti-hallucination for code tasks |
| 6 | **Output format** | `<output_format>` — positive framing (tell what TO produce); exact structure, length, sections; prefill character for JSON/YAML/SQL; LaTeX and preamble control |
| 7 | **Thinking** | `Think through this step by step` + `<thinking>/<answer>` tags for complex tasks; self-check instruction; `<thinking>` in few-shot examples for agents |
| 8 | **Examples** | `<examples>` — input/output pairs; `<bad_example>` added for ambiguous tasks to show what NOT to produce; 3–5 diverse examples for best results |
| 9 | **Tool use** | Parallel tool calling instruction; proactive vs. conservative action default; for prompts targeting agents or systems with tools |
| 10 | **Long context** | Data placed before query; multi-document XML wrapping; quote-before-answer instruction; for prompts referencing large files or documents |

Source: [Anthropic Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

---

## Contributing

steelprompt improves when people use it and report what doesn't work.

**Found a bug or unexpected behavior?** [Open an issue](https://github.com/bhutano/steelprompt/issues) — describe the prompt you typed and what you got vs. what you expected.

**Have an idea?** Open an issue with the `enhancement` label. Suggestions for new patterns, better examples, or edge cases the framework misses are all welcome.

**Want to contribute code?** See [CONTRIBUTING.md](CONTRIBUTING.md) for ground rules and testing steps.

---

## Acknowledgements

Architecture inspired by [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver). No shared code.

## License

MIT
