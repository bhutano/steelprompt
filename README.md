<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <img src="assets/banner-light.svg" alt="steelprompt" width="100%">
</picture>

<div align="center">

🌐 **English** · [中文](docs/README.zh.md) · [Español](docs/README.es.md) · [PT-BR](docs/README.pt-BR.md) · [日本語](docs/README.ja.md) · [한국어](docs/README.ko.md) · [Deutsch](docs/README.de.md) · [Français](docs/README.fr.md) · [Italiano](docs/README.it.md)

[![Version](https://img.shields.io/badge/version-0.2.0-4a9eff?style=flat-square)](https://github.com/bhutano/steelprompt)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](https://github.com/bhutano/steelprompt/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-f59e0b?style=flat-square)](https://python.org)
[![Claude Code](https://img.shields.io/badge/claude_code-2.0.22+-a78bfa?style=flat-square)](https://claude.ai/code)

**Every prompt you type is silently restructured using Anthropic's 7 official prompt engineering principles before Claude sees it.**

✦ Zero setup · ✦ No API keys · ✦ Runs inline · ✦ 4 switchable modes

</div>

---

## The problem

Claude Code is only as good as the prompts you give it. Most prompts are missing role assignment, structured context, explicit constraints, output format specification, and examples — all things Anthropic's own guidelines say dramatically improve response quality.

You could spend 10 minutes engineering every prompt manually. Or install steelprompt.

---

## How it works

steelprompt intercepts every prompt via a `UserPromptSubmit` hook and applies a 3-tier decision protocol before Claude processes it:

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
│  Restructure using 7 Anthropic principles       │
│  silently, before Claude responds               │
└─────────────────────────────────────────────────┘
```

No external API calls. Claude restructures inline during its normal inference — zero added latency, zero extra tokens billed.

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

steelprompt extends the 7 core principles with 5 context-specific patterns from the full Anthropic documentation — applied automatically when the prompt signals them:

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

### Long context ordering

When the task references long files or documents, steelprompt moves them **before** the task description inside `<context>` — matching Anthropic's guideline that long data should precede the query.

| Without steelprompt | With steelprompt |
|---|---|
| `<task>` first, then file content | file content inside `<context>` first, then `<task>` |

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
| `full` (default) | 3-tier protocol active: bypass → ask → apply 7 Anthropic principles |
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

## Bypass

steelprompt never intercepts these:

| Prefix | Behavior |
|---|---|
| `/command` | Slash commands pass through unchanged |
| `* prompt` | Explicit bypass — skip this prompt |
| `# prompt` | Explicit bypass — skip this prompt |
| < 5 words | Treated as atomic — direct response |

---

## The 7 Anthropic principles

steelprompt applies these to every non-bypassed, clear prompt:

| # | Principle | Applied as |
|---|---|---|
| 1 | **Role** | `You are a senior [domain] engineer...` |
| 2 | **Context** | `<context>` — all relevant background before the task; long files/docs placed inside `<context>` **before** the task description |
| 3 | **Task** | `<task>` — imperative mood, numbered steps for multi-step work |
| 4 | **Constraints** | `<constraints>` — what NOT to do, limits, style rules; agentic safety constraints auto-injected for destructive ops |
| 5 | **Output format** | `<output_format>` — exact structure, length, sections; prefill character anchored for JSON/YAML/SQL |
| 6 | **Chain of thought** | `Think through this step by step before answering` |
| 7 | **Examples** | `<examples>` — input/output pairs; `<bad_example>` added for ambiguous tasks to show what NOT to produce |

Source: [Anthropic Prompt Engineering Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

---

## Acknowledgements

Architecture inspired by [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver). No shared code.

## License

MIT
