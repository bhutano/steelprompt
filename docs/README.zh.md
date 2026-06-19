<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/banner-dark.svg">
  <img src="../assets/banner-light.svg" alt="steelprompt" width="100%">
</picture>

<div align="center">

🌐 [English](../README.md) · **中文** · [Español](README.es.md) · [PT-BR](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Italiano](README.it.md)

[![Version](https://img.shields.io/badge/version-0.3.0-4a9eff?style=flat-square)](https://github.com/bhutano/steelprompt/releases/tag/v0.3.0)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](https://github.com/bhutano/steelprompt/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-f59e0b?style=flat-square)](https://python.org)
[![Claude Code](https://img.shields.io/badge/claude_code-2.0.22+-a78bfa?style=flat-square)](https://claude.ai/code)

![demo](../steel_demo.gif)

**每个提示词按 Anthropic 10 条官方原则重构 — 在 Claude Code 中自动执行，在 Claude.ai 中按需触发。**

✦ 无需 API 密钥 · ✦ Claude Code + Claude.ai 网页版 · ✦ 零额外延迟 · ✦ 4 种可切换的模式

</div>

---

## 问题

Claude 的效果取决于你给它的提示有多好。大多数提示缺少角色分配、结构化上下文、显式约束、输出格式规范和示例——这些都是 Anthropic 自己的指南说能显著提高响应质量的东西。

你可以花 10 分钟手动优化每个提示。或者使用 steelprompt — 在 Claude Code 中自动运行，在 Claude.ai 中按需使用。

---

## 工作原理

steelprompt 在两个平台上运行：

- **Claude Code (CLI)** — `UserPromptSubmit` 钩子在 Claude 处理前自动拦截每个提示词。
- **Claude.ai（网页版）** — 将 `prompts/steelprompt-web.md` 粘贴到自定义指令中一次，然后使用 `/sp "提示词"` 按需工程化任意提示词。

两种方式都应用相同的 3 级决策协议：

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
│  使用 10 个 Anthropic 原则重新结构化            │
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

steelprompt 使用来自完整 Anthropic 文档的上下文特定模式扩展核心框架——当提示信号显示它们时会自动应用：

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

### 动机 / 原因

Claude 能从解释中进行泛化——steelprompt 添加请求背后的原因，而不仅仅是请求本身。带有原因的约束比单纯的规则更有效。

| 没有 steelprompt | 有 steelprompt |
|---|---|
| `永远不要使用省略号` | `永远不要使用省略号——文本转语音引擎无法朗读它们` |
| `保持回复简短` | `回复控制在 3 句话以内——输出显示在空间有限的移动端提示框中` |

---

### 格式控制（正向表述）

当指定输出格式时，steelprompt 告诉 Claude 要产生什么——而不是要避免什么。正向指令比负向指令更可靠。

```
你输入："answer in plain text, no markdown"
steelprompt 添加到 <output_format>：用流畅的散文段落书写。
                                     不要使用标题、项目符号或代码块。
```

对于无前言输出：
```
steelprompt 添加：直接回答，不要前言。
                  不要以"以下是..."、"根据..."等开头。
```

---

### Tool use 与并行调用

当提示面向具有工具的代理或系统时，steelprompt 注入并行执行和默认操作指导。

**你输入：**
```
build an agent that searches our docs, reads the top 3 results, and summarizes them
```

**steelprompt 添加到 `<constraints>`：**
```
Make all independent tool calls in parallel — search + read all 3 results simultaneously.
Never use placeholders or guess missing parameters.
By default, implement changes rather than only suggesting them.
```

---

### 思考与自我检验

对于需要多步推理或验证的任务，steelprompt 添加结构化思考和自我检验指令。

```
你输入："calculate the optimal batch size for our embedding pipeline"

steelprompt 添加：
  Reason through the problem in <thinking> tags.
  Consider: throughput, memory, API rate limits, cost per token.
  Then provide your answer in <answer> tags.
  Before finishing, verify your recommendation satisfies all constraints above.
```

---

### 长上下文排序

当任务引用长文件或文档时，steelprompt 将它们移到 `<context>` 中任务描述的**前面**——符合 Anthropic 的指南，即长数据应该在查询之前（对复杂输入可提升高达 30% 的准确率）。

```
steelprompt 还添加：Quote the relevant sections before answering.
```

| 没有 steelprompt | 有 steelprompt |
|---|---|
| `<task>` 首先，然后是文件内容 | 文件内容在 `<context>` 中首先，然后是 `<task>` |
| 查询在证据之前 | 证据在查询之前 |

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
| `full`（默认） | 3 级协议活跃：绕过 → 询问 → 应用 10 个 Anthropic 原则 |
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

## 在 Claude.ai（网页版）上使用

不用 Claude Code？你可以直接在 [claude.ai](https://claude.ai) 上获得同样的提示词工程框架 — 无需安装，无需 CLI。

**设置（一次即可）：**
1. 在浏览器中打开 [claude.ai](https://claude.ai)
2. 点击个人头像 → **设置** → **个人资料**
3. 找到 **"自定义指令"**（或 *"你希望 Claude 如何回复？"*）
4. 复制 [`prompts/steelprompt-web.md`](https://raw.githubusercontent.com/bhutano/steelprompt/master/prompts/steelprompt-web.md) 的内容并粘贴到那里 → 保存

完成。你在 Claude.ai 上写的每个提示词都会在 Claude 回复前被同样的三层协议静默重构。

**手动触发：** `/sp "你的提示词"` · **预览模式：** `/sp mode preview`

> 网页版没有钩子或工具调用 — 它作为系统提示词在 Claude.ai 的原生自定义指令中运行。

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

## 10 个 Anthropic 原则

steelprompt 将这些应用于每个清晰的、非绕过的提示：

| # | 原则 | 应用方式 |
|---|---|---|
| 1 | **角色** | `You are a senior [domain] engineer...` |
| 2 | **上下文 + 动机** | `<context>` ——任务前的所有相关背景，包括请求背后的原因；长文件/文档放在任务描述**前面** |
| 3 | **任务** | `<task>` ——祈使语气，多步工作的编号步骤；明确区分行动与建议 |
| 4 | **XML 结构** | 每个部分用描述性标签包裹（`<context>`、`<task>`、`<constraints>`、`<output_format>`、`<examples>`），以便明确解析 |
| 5 | **约束** | `<constraints>` ——不要做什么、限制、风格规则；对破坏性操作自动注入代理安全约束；代码任务的防过度热情和防幻觉约束 |
| 6 | **输出格式** | `<output_format>` ——正向表述（告诉要产生什么）；精确结构、长度、部分；JSON/YAML/SQL 的预填充字符；LaTeX 和前言控制 |
| 7 | **思考** | `Think through this step by step` + 复杂任务的 `<thinking>/<answer>` 标签；自我检验指令；代理 few-shot 示例中的 `<thinking>` |
| 8 | **示例** | `<examples>` ——输入/输出对；为模糊任务添加 `<bad_example>` 以显示不应该产生什么；3–5 个多样化示例效果最佳 |
| 9 | **Tool use** | 并行工具调用指令；主动与保守默认操作；用于面向代理或具有工具的系统的提示 |
| 10 | **长上下文** | 数据放在查询之前；多文档 XML 包裹；回答前引用相关段落的指令；用于引用大型文件或文档的提示 |

来源：[Anthropic Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

---

## 贡献

steelprompt 在人们使用并报告不起作用的内容时得到改进。

**发现了 bug 或意外行为？** [提交 issue](https://github.com/bhutano/steelprompt/issues) ——描述你输入的提示词、实际得到的结果与预期结果。

**有想法？** 用 `enhancement` 标签提交 issue。欢迎提供新模式、更好示例或框架未覆盖的边缘情况的建议。

**想贡献代码？** 请参阅 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解基本规则和测试步骤。

---

## 致谢

架构灵感来自 [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver)。没有共享代码。

## 许可证

MIT
