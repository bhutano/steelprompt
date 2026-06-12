<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/banner-dark.svg">
  <img src="../assets/banner-light.svg" alt="steelprompt" width="100%">
</picture>

<div align="center">

🌐 [English](../README.md) · [中文](README.zh.md) · [Español](README.es.md) · [PT-BR](README.pt-BR.md) · **日本語** · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Italiano](README.it.md)

[![Version](https://img.shields.io/badge/version-0.2.0-4a9eff?style=flat-square)](https://github.com/bhutano/steelprompt)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](https://github.com/bhutano/steelprompt/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-f59e0b?style=flat-square)](https://python.org)
[![Claude Code](https://img.shields.io/badge/claude_code-2.0.22+-a78bfa?style=flat-square)](https://claude.ai/code)

**あなたが入力するすべてのプロンプトは、Claude が処理する前に Anthropic の7つの公式プロンプトエンジニアリング原則に基づいて自動的に再構成されます。**

✦ セットアップ不要 · ✦ APIキー不要 · ✦ インライン実行 · ✦ 4つの切替可能なモード

</div>

---

## 問題

Claude Code の出力品質は、与えるプロンプトの質に依存します。多くのプロンプトには、ロールの割り当て、構造化されたコンテキスト、明示的な制約、出力フォーマットの指定、そして例示が欠けています——これらはすべて Anthropic 自身のガイドラインが応答品質を大幅に向上させると言っているものです。

毎回のプロンプトを手動でエンジニアリングするのに10分費やすこともできます。あるいは steelprompt をインストールすることもできます。

---

## 仕組み

steelprompt は `UserPromptSubmit` フックを通じてすべてのプロンプトを傍受し、Claude が処理する前に3段階の判定プロトコルを適用します：

```
あなたのプロンプト
    │
    ▼
┌─────────────────────────────────────────────────┐
│  ティア 1 — バイパス                            │
│  スラッシュコマンド · 5語未満 · 単一タスク      │
│  → そのまま通過                                 │
└─────────────────────────────────────────────────┘
    │ バイパスされない場合
    ▼
┌─────────────────────────────────────────────────┐
│  ティア 2 — 確認                                │
│  重要な情報が不足？                             │
│  → AskUserQuestion（的を絞った1〜2問）          │
└─────────────────────────────────────────────────┘
    │ プロンプトが明確な場合
    ▼
┌─────────────────────────────────────────────────┐
│  ティア 3 — フレームワーク適用  ← デフォルト   │
│  7つの Anthropic 原則で再構成する               │
│  Claude が応答する前に、静かに実行              │
└─────────────────────────────────────────────────┘
```

外部 API 呼び出しは一切ありません。Claude は通常の推論中にインラインで再構成します——追加レイテンシゼロ、追加トークン課金ゼロ。

---

## ティア3の実例

これが steelprompt の核心です。明確で非原子的なプロンプトはすべて自動的にここを通過します。

**あなたが入力するもの：**
```
add rate limiting to the auth endpoints
```

**steelprompt が内部で注入するもの**（`preview` モードでは実行前に確認可能）：
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

**Claude が生成するもの：** テスト付きの完全な本番対応実装——レート制限オプションに関する一般的な概要説明ではありません。

---

## 高度なパターン

steelprompt は Anthropic の完全なドキュメントから5つのコンテキスト固有のパターンで7つのコア原則を拡張します——プロンプトがそれらを示したときに自動的に適用されます：

### チェーン検出

タスクが複数の連続した操作にまたがる場合、steelprompt はチェーンを検出し、実行前に計画を表示します。

**あなたが入力するもの：**
```
auth.pyをリファクタリングして、テストを追加して、ドキュメントを更新して
```

**steelprompt がマルチステップチェーンを検出し、確認のために一時停止：**
```
Chain detected (3 prompts):
→ Prompt 1: Refactor auth.py following SOLID principles
             Produces: refactored auth.py
→ Prompt 2: Write pytest tests for the refactored code
             Uses: output of Prompt 1
→ Prompt 3: Update docs/auth.md
             Uses: output of Prompt 1 + 2
```

その後確認を求めます：**順番に実行 · 単一プロンプトとして実行 · キャンセル**

---

### エージェント安全性

タスクに不可逆な操作が含まれる場合、steelprompt は自動的に安全制約を注入します。

**あなたが入力するもの：**
```
本番データベースからすべての古いレコードを削除して
```

**steelprompt が `<constraints>` に自動追加するもの：**
```
- Show COUNT of affected rows before executing DELETE
- Scope: only rows matching the explicit filter condition
- Require explicit confirmation before the irreversible action
- Do not touch tables or columns not explicitly mentioned
```

---

### 長コンテキスト順序付け

タスクが長いファイルやドキュメントを参照する場合、steelprompt はそれらを `<context>` 内のタスク説明の**前に**移動します——長いデータはクエリより前に置くべきという Anthropic のガイドラインに従っています。

| steelprompt なし | steelprompt あり |
|---|---|
| `<task>` が先、その後にファイルの内容 | ファイルの内容が `<context>` 内で先、その後に `<task>` |

---

### 重要フォーマットのプリフィル

出力フォーマットが厳密に重要な場合（JSON、YAML、SQL）、steelprompt はプリフィルアンカーを追加します：最初のトークンから Claude を正しいフォーマットに固定するために、開始文字（`{`、`---`、`SELECT`）でレスポンスを開始します。

```
あなたが入力するもの：「この設定を解析してJSONで返して」
steelprompt が <output_format> に追加するもの：{ で応答を開始する
```

---

### 否定的な例

正しい出力フォーマットが自明でない曖昧なタスクに対して、steelprompt は `<example>` ブロックと並んで `<bad_example>` ブロックを生成します——**何を**生成しては**いけないか**を示すことで、フォーマットに敏感なタスクでのハルシネーションを減らします。

```
<example>
Input: user object → Output: {id, name, email} (no password field)
</example>
<bad_example>
Input: user object → Output: {id, name, email, password_hash} ← never expose this
</bad_example>
```

---

## ティア2の実例

重要な情報が欠けているとき、steelprompt は推測する前に確認します。

| あなたが入力するもの | steelprompt が確認すること |
|---|---|
| `"コードを改善して"` | どのファイルですか？どんな改善ですか——可読性、パフォーマンス、正確性？ |
| `"バグを修正して"` | どのバグですか？再現手順やエラーメッセージはありますか？ |
| `"authをリファクタリングして"` | 目標は何ですか？API公開向けですか、内部向けですか？動作は同一のままにすべきですか？ |
| `"アイコンの色を赤に変えて"` | *（ティア 1——原子的、直接応答）* |

---

## モード

| モード | 動作 |
|---|---|
| `full`（デフォルト） | 3段階プロトコル有効：バイパス → 確認 → 7つの Anthropic 原則を適用 |
| `preview` | 実行前にエンジニアリングされたプロンプトを表示——確認、編集、またはキャンセル |
| `ask-only` | 確認質問のみ行う；完全なフレームワークは適用しない |
| `off` | フックを完全に無効化 |

```bash
/steelprompt mode full
/steelprompt mode preview
/steelprompt mode ask-only
/steelprompt mode off
```

設定はユーザーごとに `$CLAUDE_PLUGIN_ROOT/.steelpromptrc` に保存されます。設定なし = デフォルトで `full`。

---

## プレビューモード

実行前にエンジニアリングされたプロンプトを確認したいですか？`preview` に切り替えてください：

```
/steelprompt mode preview
```

その後、通常通りにプロンプトを入力します。静かに応答する代わりに、Claude は再構成されたプロンプトを表示して確認を求めます：**実行 · 編集 · キャンセル**。

---

## 手動スキル：`/steelprompt`

任意のプロンプトを手動でエンジニアリングしたり、モードを切り替えるために使用します。

```
/steelprompt "usersテーブルにソフトデリートを追加するマイグレーション"
```

**出力：**
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

## インストール

```bash
claude plugin marketplace add bhutano/bhutano-marketplace
claude plugin install steelprompt
```

**必要条件：** Claude Code 2.0.22+ · Python 3.8+

```bash
claude --version   # Claude Code のバージョンを確認
python --version   # Python のバージョンを確認
```

---

## バイパス

steelprompt は以下を決してインターセプトしません：

| プレフィックス | 動作 |
|---|---|
| `/command` | スラッシュコマンドはそのまま通過 |
| `* prompt` | 明示的バイパス——このプロンプトをスキップ |
| `# prompt` | 明示的バイパス——このプロンプトをスキップ |
| 5語未満 | 原子的として扱われる——直接応答 |

---

## 7つのAnthropicの原則

steelprompt はバイパスされていない明確なすべてのプロンプトにこれらを適用します：

| # | 原則 | 適用方法 |
|---|---|---|
| 1 | **ロール** | `You are a senior [domain] engineer...` |
| 2 | **コンテキスト** | `<context>` ——タスク前のすべての関連背景情報；長いファイル/ドキュメントはタスク説明の**前**に `<context>` 内に配置 |
| 3 | **タスク** | `<task>` ——命令形、マルチステップ作業は番号付きステップで |
| 4 | **制約** | `<constraints>` ——やってはいけないこと、制限、スタイルルール；破壊的な操作にはエージェント安全制約が自動注入 |
| 5 | **出力フォーマット** | `<output_format>` ——正確な構造、長さ、セクション；JSON/YAML/SQL にはプリフィル文字アンカー |
| 6 | **思考の連鎖** | `Think through this step by step before answering` |
| 7 | **例示** | `<examples>` ——入力/出力ペア；曖昧なタスクには何を生成しては**いけないか**を示す `<bad_example>` を追加 |

出典：[Anthropic Prompt Engineering Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

---

## 謝辞

アーキテクチャは [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver) にインスパイアされています。共有コードはありません。

## ライセンス

MIT
