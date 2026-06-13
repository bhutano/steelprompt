<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/banner-dark.svg">
  <img src="../assets/banner-light.svg" alt="steelprompt" width="100%">
</picture>

<div align="center">

🌐 [English](../README.md) · **中文** · [Español](README.es.md) · [PT-BR](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Italiano](README.it.md)

[![Version](https://img.shields.io/badge/version-0.2.0-4a9eff?style=flat-square)](https://github.com/bhutano/steelprompt)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](https://github.com/bhutano/steelprompt/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-f59e0b?style=flat-square)](https://python.org)
[![Claude Code](https://img.shields.io/badge/claude_code-2.0.22+-a78bfa?style=flat-square)](https://claude.ai/code)

![demo](../steel_demo.gif)

**你输入的每个提示都会被自动按照 Anthropic 的 7 个官方提示工程原则重新结构化，然后才会被 Claude 看到。**

✦ 零配置 · ✦ 无需 API 密钥 · ✦ 内联运行 · ✦ 4 种可切换的模式

</div>

---

## 问题

Claude Code 的效果取决于你给它的提示有多好。大多数提示缺少角色分配、结构化上下文、显式约束、输出格式规范和示例——这些都是 Anthropic 自己的指南说能显著提高响应质量的东西。

你可以花 10 分钟手动优化每个提示。或者安装 steelprompt。

---

## 工作原理

steelprompt 通过 `UserPromptSubmit` 钩子拦截每个提示，并在 Claude 处理之前应用一个 3 级决策协议：

```
你的提示
    │
    ▼
┌─────────────────────────────────────────────────┐
│  第一级 — 绕过                                  │
│  斜杠命令 · < 5 个单词 · 原子任务              │
│  → 直接通过，不作修改                          │
└─────────────────────────────────────────────────┘
    │ 未被绕过
    ▼
┌─────────────────────────────────────────────────┐
│  第二级 — 询问                                  │
│  缺少关键信息？                                │
│  → AskUserQuestion（1-2 个有针对性的问题）      │
└─────────────────────────────────────────────────┘
    │ 提示清晰
    ▼
┌─────────────────────────────────────────────────┐
│  第三级 — 应用框架           ← 默认            │
│  使用 7 个 Anthropic 原则重新结构化             │
│  在 Claude 响应前，无声地执行                  │
└─────────────────────────────────────────────────┘
```

没有外部 API 调用。Claude 在正常推理过程中内联地重新结构化——零额外延迟，零额外计费的令牌。

---

## 第三级实战

这是 steelprompt 的核心。每个清晰的、非原子的提示都会自动通过它。

**你输入：**
```
add rate limiting to the auth endpoints
```

**steelprompt 内部注入的内容**（在 `preview` 模式下执行前可见）：
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

**Claude 产生的结果：** 一个完整的、生产就绪的实现，包括测试——不是关于速率限制选项的一般性概述。

---

## 高级模式

steelprompt 使用来自完整 Anthropic 文档的 5 个上下文特定的模式扩展了 7 个核心原则——当提示信号显示它们时会自动应用：

### 链式检测

当任务跨越多个顺序操作时，steelprompt 检测链并在执行前显示一个计划。

**你输入：**
```
refactor auth.py, add tests, update the documentation
```

**steelprompt 检测到多步骤链并暂停以获得确认：**
```
Chain detected (3 prompts):
→ Prompt 1: Refactor auth.py following SOLID principles
             Produces: refactored auth.py
→ Prompt 2: Write pytest tests for the refactored code
             Uses: output of Prompt 1
→ Prompt 3: Update docs/auth.md
             Uses: output of Prompt 1 + 2
```

然后问：**Run in sequence · Run as single prompt · Cancel**

---

### 代理安全

当任务涉及不可逆的操作时，steelprompt 会自动注入安全约束。

**你输入：**
```
delete all obsolete records from the production database
```

**steelprompt 自动添加到 `<constraints>`：**
```
- Show COUNT of affected rows before executing DELETE
- Scope: only rows matching the explicit filter condition
- Require explicit confirmation before the irreversible action
- Do not touch tables or columns not explicitly mentioned
```

---

### 长上下文排序

当任务引用长文件或文档时，steelprompt 将它们移到 `<context>` 中任务描述的**前面**——符合 Anthropic 的指南，即长数据应该在查询之前。

| 没有 steelprompt | 有 steelprompt |
|---|---|
| `<task>` 首先，然后是文件内容 | 文件内容在 `<context>` 中首先，然后是 `<task>` |

---

### 关键格式的预填充

当输出格式是严格关键的（JSON、YAML、SQL）时，steelprompt 添加一个预填充锚点：以开头字符（`{`、`---`、`SELECT`）开始响应，以从第一个令牌开始将 Claude 锁定到正确的格式。

```
你输入："parse this config and return JSON"
steelprompt 添加到 <output_format>：以 { 开始响应
```

---

### 反面示例

对于输出格式不明显的模糊任务，steelprompt 会在 `<example>` 块旁边生成 `<bad_example>` 块——显示**不应该**产生什么会减少对格式敏感任务的幻觉。

```
<example>
Input: user object → Output: {id, name, email} (no password field)
</example>
<bad_example>
Input: user object → Output: {id, name, email, password_hash} ← never expose this
</bad_example>
```

---

## 第二级实战

当缺少关键信息时，steelprompt 在猜测前会询问。

| 你输入 | steelprompt 询问 |
|---|---|
| `"improve the code"` | 哪个文件？什么样的改进——可读性、性能、正确性？ |
| `"fix the bug"` | 哪个 bug？有重现步骤或错误信息吗？ |
| `"refactor auth"` | 目标是什么？这是公共 API 还是内部的？行为应该保持相同吗？ |
| `"change icon color to red"` | *（第一级——原子的，直接响应）* |

---

## 模式

| 模式 | 行为 |
|---|---|
| `full`（默认） | 3 级协议活跃：绕过 → 询问 → 应用 7 个 Anthropic 原则 |
| `preview` | 在执行前显示工程化的提示——审查、编辑或取消 |
| `ask-only` | 仅询问澄清问题；不应用完整的框架 |
| `off` | 钩子完全禁用 |

```bash
/steelprompt mode full
/steelprompt mode preview
/steelprompt mode ask-only
/steelprompt mode off
```

配置按用户存储在 `$CLAUDE_PLUGIN_ROOT/.steelpromptrc` 中。零配置 = 默认为 `full`。

---

## 预览模式

想在运行前看到工程化的提示吗？切换到 `preview`：

```
/steelprompt mode preview
```

然后正常输入任何提示。Claude 不是无声地响应，而是会显示重新结构化的提示并问：**Run · Edit · Cancel**。

---

## 手动技能：`/steelprompt`

使用它来手动优化任何提示——或切换模式。

```
/steelprompt "migrate the users table to add soft deletes"
```

**输出：**
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

## 安装

```bash
claude plugin marketplace add bhutano/bhutano-marketplace
claude plugin install steelprompt
```

**要求：** Claude Code 2.0.22+ · Python 3.8+

```bash
claude --version   # 检查 Claude Code 版本
python --version   # 检查 Python 版本
```

---

## 绕过

steelprompt 永远不会拦截这些：

| 前缀 | 行为 |
|---|---|
| `/command` | 斜杠命令直接通过 |
| `* prompt` | 显式绕过——跳过此提示 |
| `# prompt` | 显式绕过——跳过此提示 |
| < 5 个单词 | 视为原子——直接响应 |

---

## 7 个 Anthropic 原则

steelprompt 将这些应用于每个清晰的、非绕过的提示：

| # | 原则 | 应用方式 |
|---|---|---|
| 1 | **角色** | `You are a senior [domain] engineer...` |
| 2 | **上下文** | `<context>` ——任务前的所有相关背景；长文件/文档放在 `<context>` **前面** |
| 3 | **任务** | `<task>` ——祈使语气，多步工作的编号步骤 |
| 4 | **约束** | `<constraints>` ——不要做什么、限制、风格规则；对破坏性操作自动注入代理安全约束 |
| 5 | **输出格式** | `<output_format>` ——精确结构、长度、部分；JSON/YAML/SQL 的预填充字符锚定 |
| 6 | **思维链** | `Think through this step by step before answering` |
| 7 | **示例** | `<examples>` ——输入/输出对；为模糊的任务添加 `<bad_example>` 以显示**不应该**产生什么 |

来源：[Anthropic Prompt Engineering Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

---

## 致谢

架构灵感来自 [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver)。没有共享代码。

## 许可证

MIT
