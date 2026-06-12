<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/banner-dark.svg">
  <img src="../assets/banner-light.svg" alt="steelprompt" width="100%">
</picture>

<div align="center">

🌐 [English](../README.md) · [中文](README.zh.md) · [Español](README.es.md) · **PT-BR** · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Italiano](README.it.md)

[![Version](https://img.shields.io/badge/version-0.2.0-4a9eff?style=flat-square)](https://github.com/bhutano/steelprompt)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](https://github.com/bhutano/steelprompt/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-f59e0b?style=flat-square)](https://python.org)
[![Claude Code](https://img.shields.io/badge/claude_code-2.0.22+-a78bfa?style=flat-square)](https://claude.ai/code)

**Todo prompt que você digita é reestruturado silenciosamente usando os 7 princípios oficiais de prompt engineering da Anthropic antes que Claude o veja.**

✦ Zero configuração · ✦ Sem API keys · ✦ Execução inline · ✦ 4 modos alternáveis

</div>

---

## O problema

Claude Code é tão bom quanto os prompts que você fornece. A maioria dos prompts não tem atribuição de papel, contexto estruturado, restrições explícitas, especificação de formato de saída e exemplos — tudo o que as próprias diretrizes da Anthropic dizem melhorar dramaticamente a qualidade das respostas.

Você poderia gastar 10 minutos engenheirando cada prompt manualmente. Ou instalar steelprompt.

---

## Como funciona

steelprompt intercepta cada prompt via um hook `UserPromptSubmit` e aplica um protocolo de decisão de 3 níveis antes que Claude o processe:

```
Seu prompt
    │
    ▼
┌─────────────────────────────────────────────────┐
│  NÍVEL 1 — BYPASS                               │
│  Comandos slash · < 5 palavras · tarefas        │
│  atômicas                                       │
│  → Passar sem alterações                        │
└─────────────────────────────────────────────────┘
    │ não bypassado
    ▼
┌─────────────────────────────────────────────────┐
│  NÍVEL 2 — PERGUNTAR                            │
│  Falta informação crítica?                      │
│  → AskUserQuestion (1–2 perguntas específicas)  │
└─────────────────────────────────────────────────┘
    │ prompt claro
    ▼
┌─────────────────────────────────────────────────┐
│  NÍVEL 3 — APLICAR FRAMEWORK       ← padrão    │
│  Reestruturar com 7 princípios Anthropic        │
│  silenciosamente, antes de Claude responder     │
└─────────────────────────────────────────────────┘
```

Sem chamadas de API externas. Claude reestrutura inline durante a inferência normal — zero latência adicional, zero tokens extras cobrados.

---

## Nível 3 em ação

Este é o núcleo do steelprompt. Todo prompt claro e não atômico passa por ele automaticamente.

**Você digita:**
```
add rate limiting to the auth endpoints
```

**O que steelprompt injeta internamente** (visível no modo `preview` antes da execução):
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

**O que Claude produz:** uma implementação completa e pronta para produção com testes — não uma visão geral genérica de opções de rate limiting.

---

## Padrões avançados

steelprompt estende os 7 princípios centrais com 5 padrões específicos de contexto da documentação completa da Anthropic — aplicados automaticamente quando o prompt os sinaliza:

### Detecção de cadeia

Quando uma tarefa abrange múltiplas operações sequenciais, steelprompt detecta a cadeia e exibe um plano antes de executar.

**Você digita:**
```
refactor auth.py, add tests, update the documentation
```

**steelprompt detecta uma cadeia de múltiplos passos e pausa para confirmação:**
```
Chain detected (3 prompts):
→ Prompt 1: Refactor auth.py following SOLID principles
             Produces: refactored auth.py
→ Prompt 2: Write pytest tests for the refactored code
             Uses: output of Prompt 1
→ Prompt 3: Update docs/auth.md
             Uses: output of Prompt 1 + 2
```

Então pergunta: **Run in sequence · Run as single prompt · Cancel**

---

### Segurança agêntica

Quando uma tarefa envolve operações irreversíveis, steelprompt injeta automaticamente restrições de segurança.

**Você digita:**
```
delete all obsolete records from the production database
```

**steelprompt adiciona automaticamente a `<constraints>`:**
```
- Show COUNT of affected rows before executing DELETE
- Scope: only rows matching the explicit filter condition
- Require explicit confirmation before the irreversible action
- Do not touch tables or columns not explicitly mentioned
```

---

### Ordenação de contexto longo

Quando a tarefa referencia arquivos ou documentos longos, steelprompt os move **antes** da descrição da tarefa dentro de `<context>` — seguindo a diretriz da Anthropic de que dados longos devem preceder a consulta.

| Sem steelprompt | Com steelprompt |
|---|---|
| `<task>` primeiro, depois o conteúdo do arquivo | conteúdo do arquivo dentro de `<context>` primeiro, depois `<task>` |

---

### Prefill para formatos críticos

Quando o formato de saída é rigidamente crítico (JSON, YAML, SQL), steelprompt adiciona uma âncora de prefill: inicia a resposta com o caractere de abertura (`{`, `---`, `SELECT`) para fixar Claude no formato correto desde o primeiro token.

```
Você digita: "parse this config and return JSON"
steelprompt adiciona a <output_format>: begin response with {
```

---

### Exemplos negativos

Para tarefas ambíguas onde o formato de saída correto não é óbvio, steelprompt gera blocos `<bad_example>` ao lado dos blocos `<example>` — mostrar o que **não** produzir reduz alucinações em tarefas sensíveis a formato.

```
<example>
Input: user object → Output: {id, name, email} (no password field)
</example>
<bad_example>
Input: user object → Output: {id, name, email, password_hash} ← never expose this
</bad_example>
```

---

## Nível 2 em ação

Quando informações críticas estão faltando, steelprompt pergunta antes de adivinhar.

| Você digita | steelprompt pergunta |
|---|---|
| `"improve the code"` | Qual arquivo? Que tipo de melhoria — legibilidade, performance, correção? |
| `"fix the bug"` | Qual bug? Algum passo para reproduzir ou mensagem de erro? |
| `"refactor auth"` | Qual é o objetivo? É API pública ou interna? O comportamento deve permanecer idêntico? |
| `"change icon color to red"` | *(Nível 1 — atômico, resposta direta)* |

---

## Modos

| Modo | Comportamento |
|---|---|
| `full` (padrão) | Protocolo de 3 níveis ativo: bypass → perguntar → aplicar 7 princípios Anthropic |
| `preview` | Exibe o prompt engenheirado antes de executar — revisar, editar ou cancelar |
| `ask-only` | Faz apenas perguntas de esclarecimento; não aplica o framework completo |
| `off` | Hook completamente desativado |

```bash
/steelprompt mode full
/steelprompt mode preview
/steelprompt mode ask-only
/steelprompt mode off
```

Configuração armazenada por usuário em `$CLAUDE_PLUGIN_ROOT/.steelpromptrc`. Zero configuração = padrão `full`.

---

## Modo preview

Quer ver o prompt engenheirado antes de executar? Alterne para `preview`:

```
/steelprompt mode preview
```

Então digite qualquer prompt normalmente. Em vez de responder silenciosamente, Claude mostrará o prompt reestruturado e perguntará: **Run · Edit · Cancel**.

---

## Skill manual: `/steelprompt`

Use para engenheirar manualmente qualquer prompt — ou para trocar de modo.

```
/steelprompt "migrate the users table to add soft deletes"
```

**Saída:**
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

## Instalação

```bash
claude plugin marketplace add bhutano/bhutano-marketplace
claude plugin install steelprompt
```

**Requisitos:** Claude Code 2.0.22+ · Python 3.8+

```bash
claude --version   # verificar versão do Claude Code
python --version   # verificar versão do Python
```

---

## Bypass

steelprompt nunca intercepta estes:

| Prefixo | Comportamento |
|---|---|
| `/comando` | Comandos slash passam sem alterações |
| `* prompt` | Bypass explícito — pular este prompt |
| `# prompt` | Bypass explícito — pular este prompt |
| < 5 palavras | Tratado como atômico — resposta direta |

---

## Os 7 princípios Anthropic

steelprompt aplica estes a cada prompt claro e não bypassado:

| # | Princípio | Aplicado como |
|---|---|---|
| 1 | **Papel** | `You are a senior [domínio] engineer...` |
| 2 | **Contexto** | `<context>` — todo o histórico relevante antes da tarefa; arquivos/documentos longos colocados dentro de `<context>` **antes** da descrição da tarefa |
| 3 | **Tarefa** | `<task>` — modo imperativo, passos numerados para trabalho de múltiplas etapas |
| 4 | **Restrições** | `<constraints>` — o que NÃO fazer, limites, regras de estilo; restrições de segurança agêntica injetadas automaticamente para operações destrutivas |
| 5 | **Formato de saída** | `<output_format>` — estrutura exata, tamanho, seções; caractere de prefill ancorado para JSON/YAML/SQL |
| 6 | **Cadeia de pensamento** | `Think through this step by step before answering` |
| 7 | **Exemplos** | `<examples>` — pares de entrada/saída; `<bad_example>` adicionado para tarefas ambíguas para mostrar o que NÃO produzir |

Fonte: [Anthropic Prompt Engineering Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

---

## Agradecimentos

Arquitetura inspirada por [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver). Nenhum código compartilhado.

## Licença

MIT
