<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/banner-dark.svg">
  <img src="../assets/banner-light.svg" alt="steelprompt" width="100%">
</picture>

<div align="center">

🌐 [English](../README.md) · [中文](README.zh.md) · [Español](README.es.md) · **PT-BR** · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Italiano](README.it.md)

[![Version](https://img.shields.io/badge/version-0.3.0-4a9eff?style=flat-square)](https://github.com/bhutano/steelprompt/releases/tag/v0.3.0)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](https://github.com/bhutano/steelprompt/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-f59e0b?style=flat-square)](https://python.org)
[![Claude Code](https://img.shields.io/badge/claude_code-2.0.22+-a78bfa?style=flat-square)](https://claude.ai/code)

![demo](../steel_demo.gif)

**Todo prompt reestruturado usando os 10 princípios oficiais da Anthropic — automaticamente no Claude Code, sob demanda no Claude.ai.**

✦ Sem API keys · ✦ Claude Code + Claude.ai web · ✦ Zero latência adicional · ✦ 4 modos alternáveis

</div>

---

## O problema

Claude é tão bom quanto os prompts que você fornece. A maioria dos prompts não tem atribuição de papel, contexto estruturado, restrições explícitas, especificação de formato de saída e exemplos — tudo o que as próprias diretrizes da Anthropic dizem melhorar dramaticamente a qualidade das respostas.

Você poderia gastar 10 minutos engenheirando cada prompt manualmente. Ou usar steelprompt — automático no Claude Code, sob demanda no Claude.ai.

---

## Como funciona

steelprompt funciona em duas superfícies:

- **Claude Code (CLI)** — um hook `UserPromptSubmit` intercepta cada prompt automaticamente antes que Claude o processe.
- **Claude.ai (web)** — cole `prompts/steelprompt-web.md` nas Instruções personalizadas uma vez, depois use `/sp "prompt"` para engenheirar qualquer prompt sob demanda.

Em ambos os casos, o mesmo protocolo de decisão de 3 camadas é aplicado:

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
│  Reestruturar com 10 princípios Anthropic       │
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

steelprompt estende o framework central com padrões específicos de contexto da documentação completa da Anthropic — aplicados automaticamente quando o prompt os sinaliza:

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

### Motivação / POR QUÊ

Claude generaliza a partir de explicações — steelprompt adiciona a razão por trás de uma solicitação, não apenas a solicitação em si. Uma restrição com um POR QUÊ é assimilada melhor do que uma regra isolada.

| Sem steelprompt | Com steelprompt |
|---|---|
| `NUNCA use reticências` | `Nunca use reticências — o motor de texto para fala não consegue pronunciá-las` |
| `Mantenha as respostas curtas` | `Mantenha as respostas em menos de 3 frases — a saída é exibida em um tooltip móvel com espaço limitado` |

---

### Controle de formato (enquadramento positivo)

Quando um formato de saída é especificado, steelprompt diz ao Claude o que PRODUZIR — não o que evitar. Instruções positivas são mais confiáveis do que negativas.

```
Você digita: "responda em texto simples, sem markdown"
steelprompt adiciona a <output_format>: Escreva em parágrafos de prosa fluida.
                                        Sem cabeçalhos, listas ou blocos de código.
```

Para saída sem preâmbulo:
```
steelprompt adiciona: Responda diretamente sem preâmbulo.
                      Não comece com 'Aqui está...', 'Com base em...', etc.
```

---

### Uso de ferramentas e chamadas paralelas

Quando um prompt é para um agente ou sistema com ferramentas, steelprompt injeta orientação de execução paralela e padrão de ação.

**Você digita:**
```
build an agent that searches our docs, reads the top 3 results, and summarizes them
```

**steelprompt adiciona a `<constraints>`:**
```
Make all independent tool calls in parallel — search + read all 3 results simultaneously.
Never use placeholders or guess missing parameters.
By default, implement changes rather than only suggesting them.
```

---

### Pensamento e autoavaliação

Para tarefas que exigem raciocínio de múltiplos passos ou verificação, steelprompt adiciona pensamento estruturado e uma instrução de autoavaliação.

```
Você digita: "calculate the optimal batch size for our embedding pipeline"

steelprompt adiciona:
  Reason through the problem in <thinking> tags.
  Consider: throughput, memory, API rate limits, cost per token.
  Then provide your answer in <answer> tags.
  Before finishing, verify your recommendation satisfies all constraints above.
```

---

### Ordenação de contexto longo

Quando a tarefa referencia arquivos ou documentos longos, steelprompt os move **antes** da descrição da tarefa dentro de `<context>` — seguindo a diretriz da Anthropic de que dados longos devem preceder a consulta (ganho de até 30% de precisão em entradas complexas).

```
steelprompt também adiciona: Cite as seções relevantes antes de responder.
```

| Sem steelprompt | Com steelprompt |
|---|---|
| `<task>` primeiro, depois o conteúdo do arquivo | conteúdo do arquivo dentro de `<context>` primeiro, depois `<task>` |
| Consulta antes da evidência | Evidência antes da consulta |

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
| `full` (padrão) | Protocolo de 3 níveis ativo: bypass → perguntar → aplicar 10 princípios Anthropic |
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

Se você escrever em um idioma diferente do inglês, a visualização será exibida traduzida para o seu idioma — mas **Run** sempre executa a versão em inglês, que o Claude processa com maior precisão.

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

## Usar no Claude.ai (web)

Não usa o Claude Code? Você pode obter o mesmo framework de engenharia de prompts diretamente no [claude.ai](https://claude.ai) — sem instalação, sem CLI.

**Configuração (uma única vez):**
1. Abra [claude.ai](https://claude.ai) no seu navegador
2. Clique no ícone de perfil → **Configurações** → **Perfil**
3. Encontre **"Instruções personalizadas"** (ou *"Como você gostaria que o Claude respondesse?"*)
4. Copie o conteúdo de [`prompts/steelprompt-web.md`](https://raw.githubusercontent.com/bhutano/steelprompt/master/prompts/steelprompt-web.md) e cole lá → Salvar

Pronto. Cada prompt que você escrever no Claude.ai será silenciosamente reestruturado usando o mesmo protocolo de 3 camadas antes do Claude responder.

**Ativação manual:** `/sp "seu prompt"` · **Modo preview:** `/sp mode preview`

> A versão web não tem hooks nem chamadas de ferramentas — funciona como system prompt dentro das instruções personalizadas nativas do Claude.ai.

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

## Os 10 princípios Anthropic

steelprompt aplica estes a cada prompt claro e não bypassado:

| # | Princípio | Aplicado como |
|---|---|---|
| 1 | **Papel** | `You are a senior [domínio] engineer...` |
| 2 | **Contexto + Motivação** | `<context>` — todo o histórico relevante antes da tarefa, incluindo o POR QUÊ por trás da solicitação; arquivos/documentos longos colocados **antes** da descrição da tarefa |
| 3 | **Tarefa** | `<task>` — modo imperativo, passos numerados; explícito sobre ação vs. sugestão |
| 4 | **Estrutura XML** | Cada seção envolta em tags descritivas (`<context>`, `<task>`, `<constraints>`, `<output_format>`, `<examples>`) para análise sem ambiguidade |
| 5 | **Restrições** | `<constraints>` — o que NÃO fazer, limites, regras de estilo; restrições de segurança agêntica injetadas automaticamente para operações destrutivas; anti-excesso e anti-alucinação para tarefas de código |
| 6 | **Formato de saída** | `<output_format>` — enquadramento positivo (dizer o que PRODUZIR); estrutura exata, tamanho, seções; caractere de prefill para JSON/YAML/SQL; controle de LaTeX e preâmbulo |
| 7 | **Pensamento** | `Think through this step by step` + tags `<thinking>/<answer>` para tarefas complexas; instrução de autoavaliação; `<thinking>` em exemplos few-shot para agentes |
| 8 | **Exemplos** | `<examples>` — pares de entrada/saída; `<bad_example>` adicionado para tarefas ambíguas para mostrar o que NÃO produzir; 3–5 exemplos diversos para melhores resultados |
| 9 | **Uso de ferramentas** | Instrução de chamadas paralelas de ferramentas; padrão de ação proativa vs. conservadora; para prompts direcionados a agentes ou sistemas com ferramentas |
| 10 | **Contexto longo** | Dados colocados antes da consulta; envoltório XML de múltiplos documentos; instrução de citar antes de responder; para prompts que referenciam arquivos ou documentos grandes |

Fonte: [Anthropic Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

---

## Contribuindo

steelprompt melhora quando as pessoas o usam e relatam o que não funciona.

**Encontrou um bug ou comportamento inesperado?** [Abra uma issue](https://github.com/bhutano/steelprompt/issues) — descreva o prompt que você digitou e o que obteve vs. o que esperava.

**Tem uma ideia?** Abra uma issue com o rótulo `enhancement`. Sugestões de novos padrões, melhores exemplos ou casos extremos que o framework não cobre são todos bem-vindos.

**Quer contribuir com código?** Veja [CONTRIBUTING.md](../CONTRIBUTING.md) para as regras básicas e os passos de teste.

---

## Agradecimentos

Arquitetura inspirada por [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver). Nenhum código compartilhado.

## Licença

MIT
